'''
    本模块用于提供可监听的消息类型以及可监听的事件类型
'''
# 消息类型
FriendMsg = "FriendMessage" # 好友消息
GroupMsg = "GroupMessage" # 群消息
TempMsg = "TempMessage" # 群临时会话
StrangerMsg = "StrangerMessage" # 陌生人消息
OtherClientMsg = "OtherClientMessage" # 其他客户端消息

# 事件类型
# 机器人
BotOnline = "BotOnlineEvent" # 机器人上线事件
BotOffline_Act = "BotOfflineEventActive" # 机器人主动下线事件
BotOffline_For = "BotOfflineEventForce" # 机器人被挤下线事件
BotOffline_Drop = "BotOfflineEventDropped" # 机器人因网络问题而掉线事件
BotRelogin = "BotReloginEvent" # 机器人重新登录事件

# 好友
FriendInputStatusChanged = "FriendInputStatusChangedEvent" # 好友输入状态改变事件
FriendNickChanged = "FriendNickChangedEvent" # 好友昵称改变事件

# 群
BotGroupPremissionChanged = "BotGroupPremissionChangedEvent" # 机器人群权限改变事件
BotMuted = "BotMuteEvent" # 机器人被禁言事件
BotUnmuted = "BotUnmuteEvent" # 机器人被取消禁言事件
BotJoinGroup = "BotJoinGroupEvent" # 机器人加入群事件
BotLeave_Act = "BotLeaveEventActive" # 机器人主动退出群事件
BotKicked = "BotLeaveEventKick" # 机器人被踢出群
BotLeave_Disband = "BotLeaveEventDisband" # 机器人因解散退群
GroupRecall = "GroupRecallEvent" # 群成员撤回消息事件
Nudge = "NudgeEvent" # 群戳一戳事件
GroupNameChanged = "GroupNameChangedEvent" # 群名称改变事件
GroupEntranceAnnChanged = "GroupEntranceAnnouncementChangedEvent" # 群入群公告改变事件
GroupMuteAll = "GroupMuteAllEvent" # 群全体禁言事件
GroupAllowAnonymousChat = "GroupAllowAnonymousChatEvent" # 群匿名聊天事件
GroupAllowConfessTalk = "GroupAllowConfessTalkEvent" # 群坦白说事件
GroupAllowMemberInvite = "GroupAllowMemberInviteEvent" # 群允许群成员邀请好友加群事件
MemberJoin = "MemberJoinEvent" # 群成员加入事件
MemberLeave_Kick = "MemberLeaveEventKick" # 群成员被踢出事件
MemberLeave_Quit = "MemberLeaveEventQuit" # 群成员主动离群事件
MemberCardChanged = "MemberCardChangeEvent" # 群成员名片改变事件
MemberSpeciallTitleChange = "MemberSpecialTitleChangeEvent" # 群成员特殊头衔改变事件
MemberPermissionChange = "MemberPermissionChangeEvent" # 群成员权限改变事件
MemberMute = "MemberMuteEvent" # 群成员被禁言事件
MemberUnmute = "MemberUnmuteEvent" # 群成员被取消禁言事件
MemberHonorChange = "MemberHonorChangeEvent" # 群成员称号改变事件

# 申请类
NewFriendRequest = "NewFriendRequestEvent" # 处理新的好友请求事件
MemberJoinRequest = "MemberJoinRequestEvent" # 处理新的群成员请求入群事件
BotInvitedJoinGroupRequest = "BotInvitedJoinGroupRequestEvent" # 处理机器人的邀请入群请求事件

# 其他附加类
OWNER = "OWNER" # 群主
ADMINISTRATOR = "ADMINISTRATOR" # 管理员
MEMBER = "MEMBER" # 群成员












