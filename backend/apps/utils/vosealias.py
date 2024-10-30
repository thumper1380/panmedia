import random


class VoseAlias(object):
    def __init__(self, probabilities):
        self.n = len(probabilities)
        self.U = probabilities * self.n
        self.K = list(range(self.n))

        overfull, underfull = [], []
        for i, U_i in enumerate(self.U):
            if U_i > 1:
                overfull.append(i)
            elif U_i < 1:
                underfull.append(i)

        while overfull and underfull:
            i, j = overfull.pop(), underfull.pop()
            self.K[j] = i
            self.U[i] = self.U[i] - (1 - self.U[j])
            if self.U[i] > 1:
                overfull.append(i)
            else:
                underfull.append(i)

    def sample(self):
        i = random.randint(0, self.n - 1)
        if random.random() < self.U[i]:
            return i
        else:
            return self.K[i]
