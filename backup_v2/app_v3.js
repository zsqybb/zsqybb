/**
 * LOL数据助手 - 前端交互
 * 对接后端API，显示真实数据
 */

// ==================== 工具函数 ====================

function notify(message, type = 'info') {
    const container = document.getElementById('notifications');
    const el = document.createElement('div');
    el.className = `notification ${type}`;
    el.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>${message}`;
    container.appendChild(el);
    setTimeout(() => {
        el.classList.add('removing');
        setTimeout(() => el.remove(), 300);
    }, 3500);
}

function showLoading(text = '加载中...') {
    document.getElementById('loadingText').textContent = text;
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function formatNumber(num) {
    if (num >= 10000) return (num / 10000).toFixed(1) + '万';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num.toString();
}

function formatDuration(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}分${s}秒`;
}

function formatDate(timestamp) {
    const d = new Date(timestamp);
    return `${d.getMonth()+1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2,'0')}`;
}

// ==================== 标签切换 ====================

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        const tabId = this.dataset.tab;
        document.getElementById(tabId).classList.add('active');

        const titles = {
            'self-info': '个人信息',
            'search-player': '查询他人',
            'champion-list': '英雄图鉴',
            'settings': '设置'
        };
        document.getElementById('pageTitle').textContent = titles[tabId];

        // 首次打开英雄图鉴时加载数据
        if (tabId === 'champion-list' && !window._championsLoaded) {
            loadChampions();
        }
    });
});

// ==================== LCU 连接 ====================

async function checkLcuStatus() {
    try {
        const resp = await fetch('/api/lcu/status');
        const data = await resp.json();
        const el = document.getElementById('lcuStatus');
        if (data.connected) {
            el.innerHTML = '<span class="status-dot online"></span><span>客户端已连接</span>';
        } else {
            el.innerHTML = '<span class="status-dot offline"></span><span>客户端未连接</span>';
        }
        return data.connected;
    } catch (e) {
        return false;
    }
}

async function connectLcu() {
    try {
        const resp = await fetch('/api/lcu/connect');
        const data = await resp.json();
        if (data.success) {
            notify('LCU客户端连接成功！', 'success');
            await checkLcuStatus();
        } else {
            notify(data.error || '连接失败', 'error');
        }
        return data;
    } catch (e) {
        notify('连接失败: ' + e.message, 'error');
        return { success: false };
    }
}

document.getElementById('btnLcuConnect').addEventListener('click', connectLcu);
document.getElementById('btnSettingsLcu').addEventListener('click', connectLcu);

// LCU读取
document.getElementById('btnLcuRead').addEventListener('click', async () => {
    showLoading('正在从客户端读取数据...');
    try {
        // 先连接
        const conn = await connectLcu();
        if (!conn.success) {
            hideLoading();
            notify('请先启动英雄联盟客户端', 'error');
            return;
        }

        // 等一下让连接稳定
        await new Promise(r => setTimeout(r, 500));

        const resp = await fetch('/api/lcu/current-summoner');
        const data = await resp.json();

        if (data.success) {
            notify('读取成功！', 'success');
            
            // 构建排位信息
            let rankInfo = {};
            if (data.rank_data) {
                const rd = data.rank_data;
                // 国服格式: highestRankedEntry 字段
                if (rd.highestRankedEntry) {
                    const hre = rd.highestRankedEntry;
                    rankInfo.solo = {
                        tier: hre.tier || '',
                        division: hre.division || '',
                        leaguePoints: hre.leaguePoints || 0,
                        wins: hre.wins || 0,
                        losses: hre.losses || 0,
                    };
                }
                // 国际服格式: queues 数组
                if (rd.queues && rd.queues.length) {
                    const soloQueue = rd.queues.find(q => q.queueType === 'RANKED_SOLO_5x5');
                    const flexQueue = rd.queues.find(q => q.queueType === 'RANKED_FLEX_SR');
                    if (soloQueue) {
                        rankInfo.solo = {
                            tier: soloQueue.tier || '',
                            division: soloQueue.division || '',
                            leaguePoints: soloQueue.leaguePoints || 0,
                            wins: soloQueue.wins || 0,
                            losses: soloQueue.losses || 0,
                        };
                    }
                    if (flexQueue) {
                        rankInfo.flex = {
                            tier: flexQueue.tier || '',
                            division: flexQueue.division || '',
                            leaguePoints: flexQueue.leaguePoints || 0,
                            wins: flexQueue.wins || 0,
                            losses: flexQueue.losses || 0,
                        };
                    }
                }
            }
            
            renderPlayerResult('selfResult', {
                account: {
                    puuid: data.puuid,
                    game_name: data.name,
                    tag_line: ''
                },
                summoner: {
                    name: data.name,
                    summoner_level: data.level,
                    profile_icon_id: data.profile_icon_id,
                    profile_icon_path: data.profile_icon_path,
                    puuid: data.puuid,
                },
                masteries: [],
                matches: [],
                rank: rankInfo,
            });
        } else {
            const errorMsg = data.error || '读取失败';
            // 提供更具体的错误提示
            if (errorMsg.includes('401') || errorMsg.includes('认证')) {
                notify('认证失败：请尝试重启英雄联盟客户端后重试', 'error');
            } else if (errorMsg.includes('404') || errorMsg.includes('不可用') || errorMsg.includes('未登录')) {
                notify('客户端未登录：请在英雄联盟客户端中登录账号', 'error');
            } else if (errorMsg.includes('403') || errorMsg.includes('权限')) {
                notify('权限不足：请以管理员身份运行本程序', 'error');
            } else if (errorMsg.includes('超时')) {
                notify('请求超时：客户端可能未响应，请稍后重试', 'error');
            } else {
                notify(errorMsg, 'error');
            }
        }
    } catch (e) {
        notify('读取失败: ' + e.message, 'error');
    }
    hideLoading();
});

// ==================== Riot API 查询 ====================

async function searchPlayer(gameName, tagLine, platform) {
    showLoading('正在查询玩家数据...');
    try {
        const params = new URLSearchParams({
            name: gameName,
            tag: tagLine,
            platform: platform
        });
        const resp = await fetch(`/api/player?${params}`);
        const data = await resp.json();

        if (data.success) {
            notify('查询成功！', 'success');
            return data;
        } else {
            notify(data.error || '查询失败', 'error');
            return null;
        }
    } catch (e) {
        notify('查询失败: ' + e.message, 'error');
        return null;
    } finally {
        hideLoading();
    }
}

// 个人查询
document.getElementById('btnSelfSearch').addEventListener('click', async () => {
    const name = document.getElementById('selfGameName').value.trim();
    const tag = document.getElementById('selfTagLine').value.trim();
    const platform = document.getElementById('selfPlatform').value;

    if (!name) { notify('请输入游戏名', 'error'); return; }

    const result = await searchPlayer(name, tag, platform);
    if (result) {
        renderPlayerResult('selfResult', result);
    }
});

// 查询他人
document.getElementById('btnSearchPlayer').addEventListener('click', async () => {
    const name = document.getElementById('searchGameName').value.trim();
    const tag = document.getElementById('searchTagLine').value.trim();
    const platform = document.getElementById('searchPlatform').value;

    if (!name) { notify('请输入游戏名', 'error'); return; }

    const result = await searchPlayer(name, tag, platform);
    if (result) {
        renderPlayerResult('searchResult', result);
    }
});

// ==================== 渲染玩家结果 ====================

function renderPlayerResult(containerId, data) {
    const container = document.getElementById(containerId);
    container.style.display = 'block';

    const account = data.account || {};
    const summoner = data.summoner || {};
    const masteries = data.masteries || [];
    const matches = data.matches || [];

    const iconSrc = summoner.profile_icon_path || '/static/img/profileicon/29.png';
    const summonerName = summoner.name || account.game_name || '未知';
    const level = summoner.summoner_level || 0;
    const tagLine = account.tag_line || '';

    let html = '';

    // 召唤师卡片
    html += `
    <div class="summoner-card">
        <img class="summoner-icon" src="${iconSrc}" onerror="this.src='/static/img/profileicon/29.png'" alt="头像">
        <div class="summoner-info">
            <div class="summoner-name">${summonerName}</div>
            <div class="summoner-level">Lv.${level}</div>
            ${tagLine ? `<div class="summoner-tag">#${tagLine}</div>` : ''}
            ${summoner.puuid ? `<div class="summoner-tag" style="font-size:10px;margin-top:4px">PUUID: ${summoner.puuid.substring(0,20)}...</div>` : ''}
        </div>
    </div>`;

    // 英雄熟练度
    if (masteries.length > 0) {
        html += `<div class="section-title"><i class="fas fa-star"></i> 英雄熟练度</div>`;
        html += `<div class="mastery-grid">`;
        for (const m of masteries) {
            const imgSrc = m.champion_image ? `/static/img/champion/${m.champion_image}` : '/static/img/champion/Akali.png';
            const levelClass = m.champion_level >= 7 ? 'level-7' : m.champion_level >= 6 ? 'level-6' : m.champion_level >= 5 ? 'level-5' : 'level-other';
            html += `
            <div class="mastery-item">
                <img class="mastery-champ-icon" src="${imgSrc}" onerror="this.src='/static/img/champion/Akali.png'" alt="${m.champion_name || ''}">
                <div class="mastery-info">
                    <div class="mastery-champ-name">${m.champion_name || '未知'}</div>
                    <div class="mastery-points">${formatNumber(m.champion_points)} 点</div>
                </div>
                <span class="mastery-level ${levelClass}">Lv.${m.champion_level}</span>
            </div>`;
        }
        html += `</div>`;
    }

    // 最近比赛
    if (matches.length > 0) {
        html += `<div class="section-title"><i class="fas fa-swords"></i> 最近比赛</div>`;
        html += `<div class="match-list">`;
        for (const match of matches) {
            // 找到该玩家的数据
            const myPuuid = summoner.puuid || account.puuid || '';
            const me = match.participants.find(p => p.puuid === myPuuid) || match.participants[0];
            const isWin = me.win;
            const kda = `${me.kills}/${me.deaths}/${me.assists}`;
            const kdaRatio = me.deaths === 0 ? (me.kills + me.assists) : ((me.kills + me.assists) / me.deaths).toFixed(1);
            const champImg = me.champion_image ? `/static/img/champion/${me.champion_image}` : '/static/img/champion/Akali.png';
            const champName = me.champion_name_cn || me.champion_name || '未知';

            html += `
            <div class="match-item ${isWin ? 'win' : 'loss'}">
                <img class="match-champ-icon" src="${champImg}" onerror="this.src='/static/img/champion/Akali.png'" alt="${champName}">
                <div class="match-info">
                    <div class="match-champ-name">${champName}</div>
                    <div class="match-mode">${match.game_mode || ''} · ${formatDuration(match.game_duration || 0)}</div>
                </div>
                <div class="match-kda">
                    <div class="match-kda-value ${parseFloat(kdaRatio) >= 3 ? 'good' : parseFloat(kdaRatio) < 1.5 ? 'bad' : ''}">${kda}</div>
                    <div style="font-size:11px;color:var(--text-muted)">KDA ${kdaRatio}</div>
                </div>
                <div class="match-result ${isWin ? 'win' : 'loss'}">${isWin ? '胜利' : '失败'}</div>
            </div>`;
        }
        html += `</div>`;
    }

    // 无数据提示
    if (masteries.length === 0 && matches.length === 0 && summoner) {
        html += `<div class="error-state" style="padding:20px"><i class="fas fa-info-circle" style="color:var(--info)"></i><p>召唤师信息已获取，但暂无熟练度和比赛数据</p></div>`;
    }

    // 排位信息
    const rank = data.rank || {};
    if (rank.solo || rank.flex) {
        html += `<div class="section-title"><i class="fas fa-trophy"></i> 排位信息</div>`;
        html += `<div style="display:flex;gap:16px;flex-wrap:wrap">`;
        if (rank.solo && rank.solo.tier) {
            const tierMap = {'IRON':'坚韧黑铁','BRONZE':'英勇黄铜','SILVER':'不屈白银','GOLD':'荣耀黄金','PLATINUM':'华贵铂金','EMERALD':'流光翡翠','DIAMOND':'璀璨钻石','MASTER':'超凡大师','GRANDMASTER':'傲世宗师','CHALLENGER':'最强王者'};
            const tierCn = tierMap[rank.solo.tier] || rank.solo.tier;
            const wr = rank.solo.wins + rank.solo.losses > 0 ? ((rank.solo.wins / (rank.solo.wins + rank.solo.losses)) * 100).toFixed(1) : '0';
            html += `
            <div class="ranking-card" style="flex:1;min-width:200px">
                <div class="ranking-value" style="font-size:16px;color:var(--gold)">${tierCn} ${rank.solo.division}</div>
                <div class="ranking-label">单/双排 · ${rank.solo.leaguePoints}LP</div>
                <div style="font-size:12px;color:var(--text-muted);margin-top:4px">${rank.solo.wins}胜 ${rank.solo.losses}负 · 胜率${wr}%</div>
            </div>`;
        }
        if (rank.flex && rank.flex.tier) {
            const tierMap = {'IRON':'坚韧黑铁','BRONZE':'英勇黄铜','SILVER':'不屈白银','GOLD':'荣耀黄金','PLATINUM':'华贵铂金','EMERALD':'流光翡翠','DIAMOND':'璀璨钻石','MASTER':'超凡大师','GRANDMASTER':'傲世宗师','CHALLENGER':'最强王者'};
            const tierCn = tierMap[rank.flex.tier] || rank.flex.tier;
            const wr = rank.flex.wins + rank.flex.losses > 0 ? ((rank.flex.wins / (rank.flex.wins + rank.flex.losses)) * 100).toFixed(1) : '0';
            html += `
            <div class="ranking-card" style="flex:1;min-width:200px">
                <div class="ranking-value" style="font-size:16px;color:var(--info)">${tierCn} ${rank.flex.division}</div>
                <div class="ranking-label">灵活组排 · ${rank.flex.leaguePoints}LP</div>
                <div style="font-size:12px;color:var(--text-muted);margin-top:4px">${rank.flex.wins}胜 ${rank.flex.losses}负 · 胜率${wr}%</div>
            </div>`;
        }
        html += `</div>`;
    }

    container.innerHTML = html;
}

// ==================== 英雄图鉴 ====================

let allChampions = [];
let currentRoleFilter = 'ALL';  // 分路筛选：ALL/上单/打野/中单/ADC/辅助
let currentSort = 'key';       // 排序：key/win_rate_desc/pick_rate_desc/ban_rate_desc/rank_asc/difficulty_asc

async function loadChampions() {
    try {
        // 使用 with-build 接口获取含build数据的英雄列表
        const resp = await fetch('/api/champions/with-build');
        const data = await resp.json();
        if (data.success) {
            allChampions = data.champions;
            window._championsLoaded = true;
            renderChampions();
        }
    } catch (e) {
        document.getElementById('championGrid').innerHTML =
            `<div class="error-state"><i class="fas fa-exclamation-triangle"></i><p>加载英雄列表失败</p></div>`;
    }
}

function renderChampions() {
    const grid = document.getElementById('championGrid');
    const searchText = (document.getElementById('championSearch').value || '').toLowerCase();

    let filtered = allChampions;

    // 分路筛选（基于 roles_cn）
    if (currentRoleFilter !== 'ALL') {
        filtered = filtered.filter(c => {
            const roles = (c.roles_cn || []);
            return roles.some(r => r.includes(currentRoleFilter) || r === currentRoleFilter);
        });
    }

    // 搜索
    if (searchText) {
        filtered = filtered.filter(c =>
            c.name.toLowerCase().includes(searchText) ||
            c.id.toLowerCase().includes(searchText) ||
            (c.title || '').toLowerCase().includes(searchText)
        );
    }

    // 排序
    filtered.sort((a, b) => {
        if (currentSort === 'win_rate_desc') {
            return (b.win_rate || 0) - (a.win_rate || 0);
        } else if (currentSort === 'pick_rate_desc') {
            return (b.pick_rate || 0) - (a.pick_rate || 0);
        } else if (currentSort === 'ban_rate_desc') {
            return (b.ban_rate || 0) - (a.ban_rate || 0);
        } else if (currentSort === 'rank_asc') {
            const ra = a.rank || 999, rb = b.rank || 999;
            return ra - rb;
        } else if (currentSort === 'difficulty_asc') {
            return (a.difficulty || 2) - (b.difficulty || 2);
        }
        return (a.key || 0) - (b.key || 0);  // 默认按key排序
    });

    // 更新统计
    const statsEl = document.getElementById('championStats');
    const countEl = document.getElementById('championCount');
    if (statsEl && countEl) {
        statsEl.style.display = 'flex';
        countEl.textContent = `共 ${filtered.length} 位英雄`;
    }

    if (filtered.length === 0) {
        grid.innerHTML = `<div class="error-state" style="padding:20px"><p>没有找到匹配的英雄</p></div>`;
        return;
    }

    // 难度颜色映射
    const diffClass = {1: 'easy', 2: 'medium', 3: 'hard'};
    const diffLabel = {1: '简单', 2: '中等', 3: '困难'};

    // 梯队颜色映射
    const tierColors = {0: '', 1: 'tier-1', 2: 'tier-2', 3: 'tier-3', 4: 'tier-4', 5: 'tier-5'};
    const tierLabels = {0: '', 1: 'T1', 2: 'T2', 3: 'T3', 4: 'T4', 5: 'T5'};

    grid.innerHTML = filtered.map(c => {
        const roles = (c.roles_cn || []).join('/');
        const diff = c.difficulty || 2;
        const tier = c.tier || 0;
        const tierLabel = c.tier_label || tierLabels[tier] || '';
        const winRate = c.win_rate ? c.win_rate.toFixed(1) + '%' : '';
        const pickRate = c.pick_rate ? c.pick_rate.toFixed(1) + '%' : '';
        const banRate = c.ban_rate ? c.ban_rate.toFixed(1) + '%' : '';
        const kda = c.kda ? c.kda.toFixed(2) : '';
        const rankNum = c.rank || 0;
        return `
        <div class="champion-tile ${tierColors[tier] || ''}" data-champ-id="${c.id}">
            ${tierLabel ? `<span class="champ-tier ${tierColors[tier]}">${tierLabel}</span>` : ''}
            <img src="/static/img/champion/${c.image}" onerror="this.src='/static/img/champion/Akali.png'" alt="${c.name}">
            <div class="champ-info">
                <span class="champ-name" title="${c.name}">${c.name}</span>
                ${roles ? `<span class="champ-roles">${roles}</span>` : ''}
            </div>
            <div class="champ-rates">
                ${rankNum ? `<span class="rate-rank" title="排名" style="color:var(--text-muted)">#${rankNum}</span>` : ''}
                ${winRate ? `<span class="rate-win" title="胜率">胜${winRate}</span>` : ''}
                ${pickRate ? `<span class="rate-pick" title="选取率">选${pickRate}</span>` : ''}
                ${banRate ? `<span class="rate-ban" title="禁用率">禁${banRate}</span>` : ''}
                ${kda ? `<span class="rate-kda" title="KDA" style="color:var(--accent)">KDA ${kda}</span>` : ''}
            </div>
        </div>`;
    }).join('');

    // 绑定点击事件
    grid.querySelectorAll('.champion-tile').forEach(tile => {
        tile.addEventListener('click', () => openChampionDetail(tile.dataset.champId));
    });
}

// 搜索
document.getElementById('championSearch').addEventListener('input', renderChampions);

// 分路筛选
document.querySelectorAll('.btn-filter').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        currentRoleFilter = this.dataset.role;
        renderChampions();
    });
});

// 排序
const sortEl = document.getElementById('championSort');
if (sortEl) {
    sortEl.addEventListener('change', function() {
        currentSort = this.value;
        renderChampions();
    });
}

// 英雄详情
let _currentChampBuild = null;

async function openChampionDetail(champId) {
    const modal = document.getElementById('championModal');
    const detail = document.getElementById('championDetail');

    detail.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> 加载中...</div>';
    modal.style.display = 'flex';
    _currentChampBuild = null;

    try {
        // 并行请求英雄数据和build数据
        const [respChamp, respBuild] = await Promise.all([
            fetch(`/api/champion/${champId}`),
            fetch(`/api/champion-build/${champId}`)
        ]);

        const data = await respChamp.json();
        if (!data.success) {
            detail.innerHTML = `<div class="error-state"><p>${data.error || '加载失败'}</p></div>`;
            return;
        }

        const champData = data.data || {};
        const champ = champData[champId] || Object.values(champData)[0];
        if (!champ) {
            detail.innerHTML = '<div class="error-state"><p>数据格式错误</p></div>';
            return;
        }

        // build数据
        let build = null;
        if (respBuild.ok) {
            try {
                const buildData = await respBuild.json();
                if (buildData.success) {
                    build = buildData.build;
                    _currentChampBuild = build;
                }
            } catch (e) {
                console.warn('Build数据解析失败:', e);
            }
        }

        const imgSrc = `/static/img/champion/${(champ.image && champ.image.full) || champId + '.png'}`;
        const passiveData = champ.passive || {};
        const passiveImg = `/static/img/passive/${(passiveData.image && passiveData.image.full) || champId + '_Passive.png'}`;

        // 难度星星
        const diff = (build && build.difficulty) || (champ.info && champ.info.difficulty ? Math.ceil(champ.info.difficulty / 3) : 2);
        const diffStars = '★'.repeat(diff) + '☆'.repeat(3 - diff);
        const diffLabel = ['', '简单', '中等', '困难'][diff] || '中等';

        // 分路中文
        const roleMap = { 'TOP':'上单', 'JUG':'打野', 'MID':'中单', 'ADC':'ADC', 'SUP':'辅助' };
        const rolesCn = (build && build.roles_cn) ? build.roles_cn : [];
        const rolesStr = rolesCn.length > 0 ? rolesCn.join(' / ') : (champ.tags || []).join('/');

        // 梯队标签
        const tierNum = (build && build.tier) || 0;
        const tierLabel = (build && build.tier_label) || '';
        const tierClass = tierNum ? `tier-${tierNum}` : '';
        const rankNum = (build && build.rank) || 0;
        const winRate = (build && build.win_rate) ? build.win_rate.toFixed(1) : '';
        const pickRate = (build && build.pick_rate) ? build.pick_rate.toFixed(1) : '';
        const banRate = (build && build.ban_rate) ? build.ban_rate.toFixed(1) : '';
        const kda = (build && build.kda) ? build.kda.toFixed(2) : '';

        let html = `
        <div class="champion-detail-header">
            <img src="${imgSrc}" onerror="this.src='/static/img/champion/Akali.png'" alt="${champ.name || champId}">
            <div>
                <div class="name">${champ.name || champId}
                    <span style="font-size:12px;color:var(--text-muted);font-weight:normal;margin-left:8px">${champ.title || ''}</span>
                    ${tierLabel ? `<span class="tier-badge ${tierClass}">${tierLabel}</span>` : ''}
                </div>
                <div style="display:flex;gap:12px;align-items:center;margin-top:8px;flex-wrap:wrap">
                    <span class="tag-badge" style="background:var(--gold);color:#1a1a2e"><i class="fas fa-road"></i> ${rolesStr}</span>
                    <span style="color:var(--text-muted);font-size:12px">难度: <span style="color:var(--gold)">${diffStars}</span> ${diffLabel}</span>
                    ${rankNum ? `<span style="color:var(--text-muted);font-size:12px">排名 #${rankNum}</span>` : ''}
                </div>
            </div>
        </div>

        <p style="font-size:13px;color:var(--text-secondary);line-height:1.8;margin-bottom:16px">${champ.blurb || ''}</p>`;

        // ===== 排行数据 =====
        if (winRate || pickRate || banRate) {
            html += `
        <div class="section-title"><i class="fas fa-chart-bar"></i> 韩服排位数据</div>
        <div class="ranking-cards">
            ${winRate ? `<div class="ranking-card"><div class="ranking-value ${parseFloat(winRate) >= 52 ? 'good' : parseFloat(winRate) < 48 ? 'bad' : ''}">${winRate}%</div><div class="ranking-label">胜率</div></div>` : ''}
            ${pickRate ? `<div class="ranking-card"><div class="ranking-value">${pickRate}%</div><div class="ranking-label">选取率</div></div>` : ''}
            ${banRate ? `<div class="ranking-card"><div class="ranking-value ${parseFloat(banRate) >= 10 ? 'hot' : ''}">${banRate}%</div><div class="ranking-label">禁用率</div></div>` : ''}
            ${kda ? `<div class="ranking-card"><div class="ranking-value">${kda}</div><div class="ranking-label">KDA</div></div>` : ''}
        </div>`;
        }

        // ===== 英雄属性 =====
        const info = champ.info || {};
        html += `
        <div class="champ-stats-bar">
            <div class="stat-item"><span class="stat-label">攻击</span><div class="stat-bar"><div class="stat-fill" style="width:${info.attack||0}%"></div></div></div>
            <div class="stat-item"><span class="stat-label">防御</span><div class="stat-bar"><div class="stat-fill" style="width:${info.defense||0}%"></div></div></div>
            <div class="stat-item"><span class="stat-label">魔法</span><div class="stat-bar"><div class="stat-fill" style="width:${info.magic||0}%"></div></div></div>
            <div class="stat-item"><span class="stat-label">难度</span><div class="stat-bar"><div class="stat-fill" style="width:${info.difficulty||diff*33}%"></div></div></div>
        </div>`;

        // ===== 推荐装备 =====
        if (build && build.builds) {
            const b = build.builds;
            html += `<div class="section-title"><i class="fas fa-shopping-bag"></i> 推荐装备</div>`;
            html += `<div class="build-section">`;

            if (b.starts) {
                html += `<div class="build-group"><div class="build-label">起始装备</div><div class="build-items">`;
                b.starts.forEach(item => {
                    html += `<span class="build-item">${item}</span>`;
                });
                html += `</div></div>`;
            }

            if (b.boots) {
                html += `<div class="build-group"><div class="build-label">鞋子</div><div class="build-items">`;
                b.boots.forEach(item => {
                    html += `<span class="build-item">${item}</span>`;
                });
                html += `</div></div>`;
            }

            if (b.core) {
                html += `<div class="build-group"><div class="build-label">核心装备</div><div class="build-items">`;
                b.core.forEach(item => {
                    html += `<span class="build-item core">${item}</span>`;
                });
                html += `</div></div>`;
            }

            html += `</div>`;
        }

        // ===== 推荐符文 =====
        if (build && build.runes) {
            const r = build.runes;
            html += `<div class="section-title"><i class="fas fa-gem"></i> 推荐符文</div>`;
            html += `<div class="runes-section">`;
            html += `<div class="rune-tree"><div class="rune-tree-name">${r.primary || '精密'}</div>`;
            (r.primary_runes || []).forEach(rune => {
                html += `<span class="rune-name">${rune}</span>`;
            });
            html += `</div>`;
            html += `<div class="rune-tree"><div class="rune-tree-name">${r.secondary || '坚决'}</div>`;
            (r.secondary_runes || []).forEach(rune => {
                html += `<span class="rune-name">${rune}</span>`;
            });
            html += `</div>`;
            if (r.shards) {
                html += `<div class="rune-shards">属性碎片: ${(r.shards||[]).join(' | ')}</div>`;
            }
            html += `</div>`;
        }

        // ===== 技能加点 =====
        if (build && build.skills) {
            html += `<div class="section-title"><i class="fas fa-sort-numeric-up"></i> 技能加点</div>`;
            html += `<div class="skills-order">推荐加点顺序: <span class="skills-order-text">${build.skills}</span></div>`;
        }

        // ===== 技能列表 =====
        html += `<div class="section-title"><i class="fas fa-magic"></i> 技能详情</div>`;
        html += `<div class="ability-list">`;
        
        // 被动技能（防御性检查）
        if (passiveData && passiveData.name) {
            html += `
            <div class="ability-item">
                <img src="${passiveImg}" onerror="this.src='/static/img/passive/Akali_P.png'" alt="被动">
                <div>
                    <div class="ability-name">${passiveData.name} <span style="color:var(--gold)">[被动]</span></div>
                    <div style="font-size:11px;color:var(--text-muted)">${passiveData.description || ''}</div>
                </div>
            </div>`;
        }

        const spellKeys = ['Q', 'W', 'E', 'R'];
        const spells = champ.spells || [];
        spells.forEach((spell, i) => {
            const spellImg = `/static/img/spell/${(spell.image && spell.image.full) || ''}`;
            const cd = spell.cooldown ? spell.cooldown.join('/') + 's' : '';
            const cost = spell.cost ? spell.cost.join('/') : '';
            html += `
            <div class="ability-item">
                <img src="${spellImg}" onerror="this.src='/static/img/spell/AkaliQ.png'" alt="${spell.name || ''}">
                <div>
                    <div class="ability-name">${spell.name || ''} <span style="color:var(--blue)">[${spellKeys[i] || i}]</span></div>
                    <div style="font-size:11px;color:var(--text-muted)">${spell.description || spell.tooltip || ''}</div>
                    <div style="font-size:10px;color:var(--text-muted);margin-top:4px">冷却: ${cd} | 消耗: ${cost}</div>
                </div>
            </div>`;
        });

        html += `</div>`;

        // ===== 使用技巧 =====
        if (champ.allytips && champ.allytips.length > 0) {
            html += `<div class="section-title"><i class="fas fa-lightbulb"></i> 使用技巧</div>`;
            html += `<ul class="tips-list">`;
            champ.allytips.forEach(tip => {
                html += `<li>${tip}</li>`;
            });
            html += `</ul>`;
        }

        detail.innerHTML = html;
    } catch (e) {
        console.error('英雄详情加载失败:', e);
        detail.innerHTML = `<div class="error-state"><p>加载失败: ${e.message}</p></div>`;
    }
}

document.getElementById('modalClose').addEventListener('click', () => {
    document.getElementById('championModal').style.display = 'none';
});

document.getElementById('championModal').addEventListener('click', (e) => {
    if (e.target === document.getElementById('championModal')) {
        document.getElementById('championModal').style.display = 'none';
    }
});

// ==================== API 测试 ====================

document.getElementById('btnTestApi').addEventListener('click', async () => {
    const resultEl = document.getElementById('apiTestResult');
    resultEl.textContent = '测试中...';

    try {
        const resp = await fetch('/api/player?name=Hide%20on%20bush&tag=KR1&platform=kr');
        const data = await resp.json();

        if (data.success && data.summoner) {
            resultEl.innerHTML = `<span style="color:var(--win)">✅ API可用！已获取到召唤师: ${data.summoner.name} (Lv.${data.summoner.summoner_level})</span>`;
        } else if (data.success) {
            resultEl.innerHTML = `<span style="color:var(--win)">✅ API可用！账号查询成功</span>`;
        } else {
            resultEl.innerHTML = `<span style="color:var(--loss)">❌ ${data.error || 'API测试失败'}</span>`;
        }
    } catch (e) {
        resultEl.innerHTML = `<span style="color:var(--loss)">❌ 请求失败: ${e.message}</span>`;
    }
});

// ==================== 初始化 ====================

checkLcuStatus();

// Enter键搜索
['selfGameName', 'searchGameName'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const btnId = id === 'selfGameName' ? 'btnSelfSearch' : 'btnSearchPlayer';
                document.getElementById(btnId).click();
            }
        });
    }
});

console.log('%cLOL数据助手 v2.0 已加载', 'color: #c89b3c; font-size: 16px; font-weight: bold');
