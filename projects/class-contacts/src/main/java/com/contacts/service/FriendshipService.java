package com.contacts.service;

import com.contacts.dao.FriendshipDao;
import com.contacts.dao.LogDao;
import com.contacts.entity.Friendship;

import java.util.List;

/**
 * 好友模块业务逻辑层（核心修复版：保证社交关系双向对称与操作审计）
 */
public class FriendshipService {
    
    private FriendshipDao friendshipDao = new FriendshipDao();
    private LogDao logDao = new LogDao();

    /**
     * 发起好友申请（升级：细化返回值状态，防止重复骚扰）
     * @return 1:发送成功, 0:数据库写入失败, -1:不能加自己, -2:已经是好友, -3:申请已经在审批中
     */
    public int sendFriendRequest(int userId, int friendId, String ipAddress) {
        if (userId == friendId) {
            return -1; // 禁止添加自己
        }
        
        // 1. 必须使用双向检查查询：是否已经是正式好友 (status = 1)
        if (friendshipDao.isFriend(userId, friendId)) {
            return -2; // 已是好友
        }
        
        // 2. 检查是否已经存在待审批的申请 (status = 0)，防止重复发骚扰请求或抛出数据库主键冲突
        if (hasPendingRequest(userId, friendId)) {
            return -3; // 正在审核中
        }

        // 3. 正常发起申请（调用我们在第四部分写好的智能状态机方法）
        boolean success = friendshipDao.sendRequest(userId, friendId);
        if (success) {
            if (logDao != null && ipAddress != null) {
                logDao.addLog(userId, "发出好友申请 -> 接收人ID:" + friendId, ipAddress);
            }
            return 1;
        }
        return 0; // 插入数据库失败
    }

    /**
     * @description 核心修复：审批好友申请。通过审批时，自动为双方建立对称的互通关系记录
     * @param currentUserId 当前操作审批的用户ID（接收方）
     * @param requesterId   申请发起人ID
     * @param status        1:通过, 2:拒绝
     */
    public boolean auditFriendRequest(int currentUserId, int requesterId, int status, String ipAddress) {
        if (status != 1 && status != 2) return false;
        
        // 1. 更新原申请的状态 (发起人=requesterId, 审批人=currentUserId)
        // 注意：在第四部分升级后，当 status==1 时，DAO 内部其实已经会触发一次双向闭环
        boolean updateSuccess = friendshipDao.updateFriendStatus(requesterId, currentUserId, status);
        
        if (updateSuccess && status == 1) {
            // 2. 【关键双保险修复】如果是“同意”操作，必须确保数据库中有对应的对称反向映射
            // 采用强制补齐反向关系记录的做法，建立真正的双向社交图谱
            if (!recordExists(currentUserId, requesterId)) {
                // 如果对方没有任何记录，主动插入反向对等关系 (通过转调 sendRequest/accept 实现)
                friendshipDao.acceptRequest(requesterId, currentUserId);
            } else {
                // 如果记录存在但状态不对，强制更新反向映射为已正式同意
                friendshipDao.updateFriendStatus(currentUserId, requesterId, 1);
            }
            
            if (logDao != null && ipAddress != null) {
                logDao.addLog(currentUserId, "通过了用户ID:" + requesterId + " 的好友申请，正式缔结好友", ipAddress);
            }
        } else if (updateSuccess && status == 2) {
            if (logDao != null && ipAddress != null) {
                logDao.addLog(currentUserId, "委婉拒绝了用户ID:" + requesterId + " 的好友申请", ipAddress);
            }
        }
        return updateSuccess;
    }

    /**
     * 获取好友列表（双向对称查询）
     */
    public List<Friendship> getFriendList(int userId) {
        return friendshipDao.getFriendList(userId);
    }

    /**
     * 删除好友（双向物理解除）
     */
    public boolean removeFriend(int userId, int friendId, String ipAddress) {
        boolean success = friendshipDao.deleteFriend(userId, friendId);
        if (success) {
            if (logDao != null && ipAddress != null) {
                logDao.addLog(userId, "删除了好友(用户ID: " + friendId + ")", ipAddress);
            }
        }
        return success;
    }

    /**
     * 判断是否为好友
     */
    public boolean isFriend(int userId, int friendId) {
        return friendshipDao.isFriend(userId, friendId);
    }

    /**
     * 获取待验证的好友申请列表
     */
    public List<Friendship> getPendingRequests(int userId) {
        return friendshipDao.getPendingRequests(userId);
    }

    // ==================== 私有辅助方法（适配方案需求，避免增加DAO负担或报编译错误） ====================

    /**
     * 辅助检查：两用户之间是否存在待审批的申请 (status = 0)
     */
    private boolean hasPendingRequest(int userId1, int userId2) {
        // 检查是否有发给我的，或者我发给对方的待验证请求
        List<Friendship> list1 = friendshipDao.getPendingRequests(userId2); // userId1 发给 userId2 的
        for (Friendship f : list1) {
            if (f.getUserId() == userId1) return true;
        }
        List<Friendship> list2 = friendshipDao.getPendingRequests(userId1); // userId2 发给 userId1 的
        for (Friendship f : list2) {
            if (f.getUserId() == userId2) return true;
        }
        return false;
    }

    /**
     * 辅助检查：A对B是否有底层的关系映射记录（不管状态是 0 还是 1）
     */
    private boolean recordExists(int userId, int friendId) {
        // 如果已经是好友，一定存在记录
        if (friendshipDao.isFriend(userId, friendId)) return true;
        // 如果有待审批申请，也说明存在记录
        return hasPendingRequest(userId, friendId);
    }
    
    /**
     * 【新增方法】判断某人是否向另一人发送过待验证的好友申请 (单向校验)
     * 参数使用 Integer 包装类，完美兼容 Servlet 中的 (int, Integer) 和 (Integer, int) 调用
     */
    public boolean hasSentRequest(Integer senderId, Integer receiverId) {
        // 安全防御：防止未登录或找不到用户时触发 NullPointerException
        if (senderId == null || receiverId == null) {
            return false;
        }
        return friendshipDao.hasSentRequest(senderId, receiverId);
    }
}