const { WebcastPushConnection } = require('./node/node_modules/tiktok-live-connector');
const fs = require('fs');
const WebSocket = require('./node/node_modules/ws');

let username
let sessionId
let connectedClient = null;
let TryRecon = true
let TryNumm = 0;
const MaxTry = 100;


function auth_json() {
    try {
        const data = fs.readFileSync(`${process.env.APPDATA}/VibesBot/web/src/auth/auth.json`, 'utf8');

        parse_auth = JSON.parse(data)

        username = parse_auth.USERNAME
        sessionId = parse_auth.SESSIONID

    } catch (err) {
        console.error('Erro ao ler o arquivo JSON:', err);
    }
}

auth_json();


const wss = new WebSocket.Server({ port: 7788 });

wss.on('connection', (ws) => {

    if (connectedClient === null) {

        connectedClient = ws;
        ws.on('close', () => {
            connectedClient = null;
        });

        const pingInterval = setInterval(() => {
            if (connectedClient && connectedClient.isAlive === false) {
                clearInterval(pingInterval);
                connectedClient.terminate();
            } else if (connectedClient) {
                connectedClient.isAlive = false;
                connectedClient.ping('', false, 'utf8');
            }
        }, 5000);

        connectedClient.on('pong', () => {
            connectedClient.isAlive = true;
        });

        connectedClient.on('message', (message) => {

            const parsedMessage = JSON.parse(message);

            if (parsedMessage.type === 'Close') {

                message = {
                    type: "close_event",
                    message: `close`,
                };

                sendWebsocket(message);

                TryRecon = false;
                connectedClient.terminate();
                tiktokLiveConnection.disconnect();
                process.exit(1);

            }
        });

    } else {
        ws.terminate();
    }

});

function sendWebsocket(message) {

    console.log(message)

    if (connectedClient && connectedClient.readyState === WebSocket.OPEN) {
        connectedClient.send(JSON.stringify(message));
    }
}

let tiktokLiveConnection = new WebcastPushConnection(username, {

    processInitialData: false,
    enableExtendedGiftInfo: true,
    enableWebsocketUpgrade: true,
    requestPollingIntervalMs: 2000,
    clientParams: {
        "app_language": "pt-BR",
        "device_platform": "web"
    },
    sessionId: sessionId
});


async function RoomInfo() {

    try {
        const roomInfo = await tiktokLiveConnection.getRoomInfo();
        const totalfollows = roomInfo.owner.follow_info.follower_count;

        return totalfollows

    } catch (err) {

        message = {
            type: "error_event",
            message: `Erro ${err}`,
        };

        sendWebsocket(message);

        return 0
    }
}

async function getGiftsData() {
    
    try {
        const giftList = await tiktokLiveConnection.getAvailableGifts();

        const data = giftList.reduce((acc, obj) => {

            acc[obj.id] = {
                name: obj.name,
                name_br: "",
                value: obj.diamond_count,
                id: obj.id,
                icon: obj.icon.url_list,
                audio: "",
                status: 0,
                volume: 50,
                "points-global": 1,
                points: 0,
                time: "00:00:00",
                keys: [],
                key_status: 0,
                key_time: 0,
                status_subathon: 0,
                video_status: 0,
                video: "",
                video_time: 0
            };

            return acc;

        }, {});

        const jsonData = JSON.stringify(data, null, 2);

        return jsonData;

    } catch (err) {

        message = {
            type: "error_event",
            message: `Erro ${err}`,
        };

        sendWebsocket(message);

        data = {}
        return JSON.stringify(data, null, 2);
    }
}

async function tryReconnect() {
    
    try {
        const state = await tiktokLiveConnection.connect();

        folloersinfo = await RoomInfo();

        giftinfo = await getGiftsData();

        const message = {
            type: "connect_event",
            room_id: `${state.roomId}`,
            giftdata: giftinfo,
            followers: folloersinfo
        };

        sendWebsocket(message);

    } catch (err) {

        TryNumm++;

        if (err != "Error: LIVE has ended"){

            const message = {
                type: "error_event",
                message: `Erro ao reconectar ${err}. Tentativa ${TryNumm}/${MaxTry}`,
            };
    
            sendWebsocket(message);
        }

        if (TryNumm < MaxTry) {

            setTimeout(tryReconnect, 10000);

        } else {
            const errorMessage = {
                type: "error_event",
                message: `Número máximo de tentativas de reconexão atingido, Reinicie o VibesBot para tentar novamente ou entre em contato com o suporte via discord.`,
            };

            sendWebsocket(errorMessage);
        }
    }
}

tiktokLiveConnection.on('disconnected', () => {
    try {

        const message = {
            type: "disconnect_event",
        };
        sendWebsocket(message);

        if (TryRecon == true) {
            tryReconnect();
        }
    } catch (error) {

        if (err != "Error: LIVE has ended"){

            const message = {
                type: "error_event",
                message: `Erro ao reconectar ${err}. Tentativa ${TryNumm}/${MaxTry}`,
            };
    
            sendWebsocket(message);
        }
    }
});

tiktokLiveConnection.on('chat', data => {

    try {

        const is_following = data.followInfo.followStatus > 0 ? true : false;
        
        const message = {
            type: "comment_event",
            userid: data.userId,
            username: data.uniqueId,
            nickname: data.nickname,
            comment: data.comment,
            is_following: is_following,
            is_moderator: data.isModerator,
            is_subscriber: data.isSubscriber,
            badges_list: data.userBadges,
            is_top_gifter: data.topGifterRank,
            profilePictureUrl: data.profilePictureUrl,
        };

        sendWebsocket(message);

    } catch (error) {

        message = {
            type: "error_event",
            message: `Erro chat ${err}`,
        };
        sendWebsocket(message);
    }
});

tiktokLiveConnection.on('gift', data => {

    try {

        const streaking = data.gift.repeat_end == 1 ? false : true;
        const streakable = data.gift.gift_type == 1 ? true : false;
        const is_following = data.followInfo.followStatus > 0 ? true : false;

        const message = {
            type: "gift_event",
            userid: data.userId,
            username: data.uniqueId,
            nickname: data.nickname,
            is_following: is_following,
            is_moderator: data.isModerator,
            is_subscriber: data.isSubscriber,
            giftId: data.giftId,
            gift_diamonds: data.diamondCount,
            gift_name: data.giftName,
            streakable: streakable,
            streaking: streaking,
            giftcount: data.gift.repeat_count,
            profilePictureUrl: data.profilePictureUrl,
        };

        sendWebsocket(message);
        
    } catch (error) {

        message = {
            type: "error_event",
            message: `Erro gift ${err}`,
        };

        sendWebsocket(message);
    }
});

tiktokLiveConnection.on('like', data => {

    try {

        const is_following = data.followInfo.followStatus > 0 ? true : false;

        const message = {
            type: "like_event",
            userid: data.userId,
            username: data.uniqueId,
            nickname: data.nickname,
            likes: data.likeCount,
            total_likes: data.totalLikeCount,
            profilePictureUrl: data.profilePictureUrl,
            is_following: is_following,
            is_moderator: data.isModerator,
            is_subscriber: data.isSubscriber,
        };
        sendWebsocket(message);

    } catch (error) {

        message = {
            type: "error_event",
            message: `Erro gift ${err}`,
        };
        sendWebsocket(message);
    }
});

tiktokLiveConnection.on('member', data => {

    try {
        const message = {
            type: "join_event",
            userid: data.userId,
            username: data.uniqueId,
            nickname: data.nickname,
            profilePictureUrl: data.profilePictureUrl,
        };
        sendWebsocket(message);

    } catch (error) {
        message = {
            type: "error_event",
            message: `Erro gift${err}`,
        };
        sendWebsocket(message);
    }
});

tiktokLiveConnection.on('roomUser', data => {

    try {
        const top_viewers = data.topViewers;
        const viewerCount = data.viewerCount;
        let user_info;

        if (viewerCount != null && top_viewers.length > 0) {
            const user = top_viewers[0];
            userinfo = user.user;

            user_info = {
                userid: data.userId,
                username: data.uniqueId,
                nickname: data.nickname,
                profilePictureUrl: userinfo.profilePictureUrl,
                followRole: userinfo.followRole,
                userBadges: userinfo.userBadges,
                isModerator: userinfo.isModerator,
                isNewGifter: userinfo.isNewGifter,
                isSubscriber: userinfo.isSubscriber,
                topGifterRank: userinfo.topGifterRank,
                coinCount: user.coinCount
            };

            const message = {
                type: "viewer_event",
                viewer_count: viewerCount,
                top_viewer: user_info,
            };
            sendWebsocket(message);
        }
    } catch (error) {
        message = {
            type: "error_event",
            message: `Erro ${err}`,
        };
        sendWebsocket(message);
    }
});

tiktokLiveConnection.on('envelope', data => {
    try {
        const message = {
            type: "envelope_event",
            userid: data.userId,
            username: data.uniqueId,
            nickname: data.nickname,
            profilePictureUrl: data.profilePictureUrl,
            followRole: data.followRole,
            userBadges: data.userBadges,
            isModerator: data.isModerator,
            isNewGifter: data.isNewGifter,
            isSubscriber: data.isSubscriber,
            topGifterRank: data.topGifterRank,
            coinCount: data.coinCount,
            canOpen: data.canOpen,
        };
        sendWebsocket(message);
    } catch (error) {
        message = {
            type: "error_event",
            message: `Erro envelope ${err}`,
        };
        sendWebsocket(message);
    }
});

tiktokLiveConnection.on('share', (data) => {
    try {
        
        const is_following = data.followInfo.followStatus > 0 ? true : false;

        const message = {
            type: "share_event",
            userid: data.userId,
            username: data.uniqueId,
            nickname: data.nickname,
            profilePictureUrl: data.profilePictureUrl,
            is_following: is_following,
            is_moderator: data.isModerator,
            is_subscriber: data.isSubscriber,
        };
        sendWebsocket(message);
    } catch (error) {
        message = {
            type: "error_event",
            message: `Erro share ${err}`,
        };
        sendWebsocket(message);
    }
});

tiktokLiveConnection.on('follow', async (data) => {
    try {

        const is_following = data.followInfo.followStatus > 0 ? true : false;

        const message = {
            type: "follow_event",
            userid: data.userId,
            username: data.uniqueId,
            nickname: data.nickname,
            profilePictureUrl: data.profilePictureUrl,
            is_following: is_following,
            is_moderator: data.isModerator,
            is_subscriber: data.isSubscriber,
        };
        sendWebsocket(message);
    } catch (error) {
        message = {
            type: "error_event",
            message: `Erro follow ${err}`,
        };
        sendWebsocket(message);
    }
});

tryReconnect()