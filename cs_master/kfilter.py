import numpy as np
from filterpy.kalman import KalmanFilter


def motion_translation_matrix(dt):
    return np.array([[1, dt, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, dt],
                     [0, 0, 0, 1]])


def mouse_matrix(dt):
    return np.array([[1, 0],
                     [0, 1]])


# 创建卡尔曼滤波器
motion_kf = KalmanFilter(dim_x=4, dim_z=2)

# 定义状态转移矩阵
dt = 0.01  # 时间步长
motion_kf.F = motion_translation_matrix(dt)

# 定义测量矩阵
motion_kf.H = np.array([[1, 0, 0, 0],
                        [0, 0, 1, 0]])

# 定义过程噪声协方差矩阵
q = 0.1  # 过程噪声方差
motion_kf.Q = np.array([[q, 0, 0, 0],
                        [0, 10000 * q, 0, 0],
                        [0, 0, q, 0],
                        [0, 0, 0, 10000 * q]])

# 定义测量噪声协方差矩阵
r = 2  # 测量噪声方差
motion_kf.R = np.array([[r, 0],
                        [0, 2 * r]])

# 初始化状态向量和协方差矩阵
motion_kf.x = np.array([0, 0, 0, 0])  # 初始状态（位置和速度）
motion_kf.P = np.eye(4)  # 初始协方差矩阵


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # 生成模拟数据
    np.random.seed(0)
    n_samples = 20
    t = np.arange(n_samples)
    true_position = np.concatenate((10 * t[:10], 10 * t[10] + 0 * t[10:n_samples]), axis=0)  # 真实位置
    true_v = np.concatenate((10 + np.zeros_like(t[:10]), 0 * np.zeros_like(t[10:n_samples])), axis=0)  # 真实速度
    pred_true_v = np.concatenate((true_v[2:], [0, 0]), axis=0)
    pred_true_position = np.concatenate((true_position[2:], [0, 0]), axis=0)
    measurements = true_position + np.random.randn(n_samples) * r  # 测量位置

    # 保存滤波结果
    filtered_position = []
    filtered_velocity = []
    pred_position = []

    # 执行滤波
    for z in measurements:
        motion_kf.predict()
        motion_kf.update(np.array([z, z]))
        print(motion_kf.x.reshape((-1, 1)))
        pred = np.array([[1, 2 * dt, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, 1, 2 * dt],
                         [0, 0, 0, 1]]) @ motion_kf.x.reshape((-1, 1))
        filtered_position.append(motion_kf.x[0])
        filtered_velocity.append(motion_kf.x[1])
        pred_position.append(pred[0])

    # 绘制结果
    plt.figure()
    plt.plot(t, true_position, label='True Position')
    plt.plot(t, pred_true_position, label='Predicted True Position')
    plt.plot(t, true_v / dt, label='True Velocity')
    plt.plot(t, pred_true_v / dt, label='Predicted True Velocity')
    plt.plot(t, measurements, 'ro', label='Measurements')
    plt.plot(t, filtered_position, 'g-', label='Filtered Position')
    plt.plot(t, filtered_velocity, 'b-', label='Filtered Velocity')
    plt.plot(t, pred_position, 'k-', label='Predicted Position')
    plt.xlabel('Tick')
    plt.ylabel('Position / Velocity')
    plt.title('Kalman Filter')
    plt.legend()
    plt.show()
