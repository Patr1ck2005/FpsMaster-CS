from scipy.interpolate import interp1d
import numpy as np

m4a1 = [[0, 0.1, 0.64, 0.72, 1.5, 2.2], [0, 0, 0, -10, 12, 12], [0, -4, -20, -35, -35, -35]]
m4a1_x = interp1d(x=m4a1[0], y=m4a1[1])
m4a1_y = interp1d(x=m4a1[0], y=m4a1[2])

ak47 = [[0, 0.1, 0.4, 0.68, 1.1, 1.2, 2, 2.44, 2.95],
        [0, 0, 0, -14, 18, 20, -17, -15, 30],
        [-1, -7, -28, -53, -58, -58, -65, -63, -57]]
ak47_x = interp1d(x=ak47[0], y=ak47[1])
ak47_y = interp1d(x=ak47[0], y=ak47[2])

negev = [[0, 0.5, 10], [0, 0, 0], [0, -55, -55]]
negev_x = interp1d(x=negev[0], y=negev[1])
negev_y = interp1d(x=negev[0], y=negev[2])


class RecoilCurve:
    @staticmethod
    def ak47(time):
        time = min(time, ak47[0][-1])
        return ak47_x(time), ak47_y(time)

    @staticmethod
    def m4a1(time):
        time = min(time, m4a1[0][-1])
        return m4a1_x(time), m4a1_y(time)

    @staticmethod
    def negev(time):
        time = min(time, negev[0][-1])
        return negev_x(time), negev_y(time)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    bullet = np.linspace(0, 29, 30)
    tick = bullet*(3/30)
    bullet_x = ak47_x(tick)
    bullet_y = ak47_y(tick)
    plt.plot(bullet_x, bullet_y, '--o', label='Bullet', alpha=0.5)
    plt.plot(ak47[1], ak47[2], label='ak47')
    plt.show()
