import cv2
from polynomials.tchebichef import tch_ploy
from moments.plain_moments import Moment
from encryption.vhe import *


class Cipher_Moment:

    def __init__(self, type, v, Q):
        self.type = type
        self.npoly = type.npoly
        self.mpoly = type.mpoly
        self.v = v
        self.Q = Q

    # PPQDOM
    def cipher_qua_moment(self, eimg, N, npoly=None, mpoly=None):
        """
        Input a gray image
        Output ciphertext moments
        """

        if npoly is not None:
            self.npoly = npoly

        if mpoly is not None:
            self.mpoly = mpoly

        height, width, _ = eimg.shape

        quan_npoly = np.round(self.Q * self.npoly).astype(np.int64)
        quan_mpoly = np.round(self.Q * self.mpoly).astype(np.int64)

        m0 = self.type.gray_moment(eimg[:, :, 0], quan_npoly, quan_mpoly)
        m1 = self.type.gray_moment(eimg[:, :, 1], quan_npoly, quan_mpoly)
        m2 = self.type.gray_moment(eimg[:, :, 2], quan_npoly, quan_mpoly)
        m3 = self.type.gray_moment(eimg[:, :, 3], quan_npoly, quan_mpoly)
        m4 = self.type.gray_moment(eimg[:, :, 4], quan_npoly, quan_mpoly)
        m5 = self.type.gray_moment(eimg[:, :, 5], quan_npoly, quan_mpoly)
        m6 = self.type.gray_moment(eimg[:, :, 6], quan_npoly, quan_mpoly)
        m7 = self.type.gray_moment(eimg[:, :, 7], quan_npoly, quan_mpoly)

        cipher_qua_moment = np.ones((height, width, 2 * N), np.object)

        for n in range(height):
            for m in range(width):
                cipher_qua_moment[n, m] = [m0[n, m], m1[n, m], m2[n, m], m3[n, m],
                                      m4[n, m], m5[n, m], m6[n, m], m7[n, m]]
        return cipher_qua_moment

    #PPQCIR
    def cipher_recons_image(self, cipher_moment, n, m, npoly=None, mpoly=None):
        """
        Get ciphertext reconstruction image
        """

        if npoly is not None:
            self.npoly = npoly

        if mpoly is not None:
            self.mpoly = mpoly

        height, width, _ = cipher_moment.shape

        quan_npoly = np.round(self.Q * self.npoly).astype(np.int64)
        quan_mpoly = np.round(self.Q * self.mpoly).astype(np.int64)

        cipher_image = np.zeros((height, width, 8), np.object)

        channel0 = self.type.inv_gray_moment(cipher_moment[:, :, 0], n, m, npoly=quan_npoly,
                                             mpoly=quan_mpoly, flag=False)
        channel1 = self.type.inv_gray_moment(cipher_moment[:, :, 1], n, m, npoly=quan_npoly,
                                             mpoly=quan_mpoly, flag=False)
        channel2 = self.type.inv_gray_moment(cipher_moment[:, :, 2], n, m, npoly=quan_npoly,
                                             mpoly=quan_mpoly, flag=False)
        channel3 = self.type.inv_gray_moment(cipher_moment[:, :, 3], n, m, npoly=quan_npoly,
                                             mpoly=quan_mpoly, flag=False)
        channel4 = self.type.inv_gray_moment(cipher_moment[:, :, 4], n, m, npoly=quan_npoly,
                                             mpoly=quan_mpoly, flag=False)
        channel5 = self.type.inv_gray_moment(cipher_moment[:, :, 5], n, m, npoly=quan_npoly,
                                             mpoly=quan_mpoly, flag=False)
        channel6 = self.type.inv_gray_moment(cipher_moment[:, :, 6], n, m, npoly=quan_npoly,
                                             mpoly=quan_mpoly, flag=False)
        channel7 = self.type.inv_gray_moment(cipher_moment[:, :, 7], n, m, npoly=quan_npoly,
                                             mpoly=quan_mpoly, flag=False)

        for y in range(height):
            for x in range(width):
                cipher_image[y, x] = [channel0[y, x], channel1[y, x], channel2[y, x], channel3[y, x],
                                      channel4[y, x], channel5[y, x], channel6[y, x], channel7[y, x]]
        return cipher_image

    def decrypt_cipher_moments(self, cipher_moments, S):
        h, w, c = cipher_moments.shape
        plain_moments = np.zeros((h, w, 4))
        for n in range(h):
            for m in range(w):
                plain_moments[n, m] = self.v.decrypt(S, cipher_moments[n, m]) / math.sqrt(3) / self.Q ** 2
        return plain_moments

    def decrypt_cipher_image(self, cipher_image, S):
        h, w, c = cipher_image.shape
        plain_image = np.zeros((h, w, 3))
        for y in range(h):
            for x in range(w):
                plain_image[y, x] = self.v.decrypt(S, cipher_image[y, x])[1:4] / 3 / Q ** 4
        plain_image = np.abs(np.round(plain_image)).astype(np.uint8)
        return plain_image


if __name__ == '__main__':
    print("Initial parameters... ")
    N = 4
    stdev = 3.2
    w = generate_prime(78)
    bound = 200
    l = 180
    q = generate_prime(80)
    U = np.array([[0, 1, 1, 1], [-1, 0, -1, 1], [-1, 1, 0, -1], [-1, -1, 1, 0]])
    v = VHE(l, w, bound, stdev, q)
    T = v.get_random_matrix(N, N)
    S, I = v.get_secret_key(T)
    SS = np.dot(U, S)
    SSS = np.dot(U, SS)
    M = v.get_public_key(I, T)

    Q = pow(2, 10)

    image = cv2.imread('../data/baboon.ppm')
    if image.shape[0] > 256:
        image = cv2.resize(image, (256, 256))

    h, w, _ = image.shape
    type = Moment(tch_ploy(h), tch_ploy(w))
    cm = Cipher_Moment(type, v, Q)

    print("image encryption...")
    cipher_image = v.encrypt_image(image, N, M)
    # cv2.imshow("deimg", v.decrypt_image(cipher_image, S))
    # cv2.waitKey()

    print("test cipher quaternion moments(PPQDOM)...")
    # print(type.qua_moment(image))
    cipher_moments = cm.cipher_qua_moment(cipher_image, N)
    # print(cm.decrypt_cipher_moments(cipher_moments, SS))

    print("test cipher image reconstruction...(PPQCIR)")
    cipher_image = cm.cipher_recons_image(cipher_moments, 256, 256)
    cv2.imshow("dst", cm.decrypt_cipher_image(cipher_image, SSS))
    cv2.waitKey()

