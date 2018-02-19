from primes import get_random_prime, get_random_number, gcd, solve_mod_problem
from hashlib import sha256


class RSA:
    INITIAL_STATE = 11
    def __init__(self, exponent, modulus, d=None):
        self.exponent = exponent
        self.modulus = modulus
        self.block_size = (len(bin(self.modulus)) - 2)/8*8
        self.d = d

    @classmethod
    def get_random_rsa(cls, bits=512, num_prime_checks=121):
        assert bits % 8 == 0 and bits >= 8
        a = b = 0
        while a==b:
            a, b = [get_random_prime(bits/2+1, final_num_checks=num_prime_checks) for _ in xrange(2)]
        modulus = a * b
        period = (a-1)*(b-1)*gcd(a-1, b-1)  # anything^(1+period) == anything (mod modulus)
        exponent = period
        while gcd(exponent, period) != 1:
            exponent = get_random_number(16)+2**16
        d, _ = solve_mod_problem(exponent, period, 1)

        return cls(exponent, modulus, d)

    def recover_ab(self, brute_force=False):
        if self.d is None:
            if not brute_force:
                raise ValueError('private key not present, factorisation of modulus required - quiting. Set brute_force to force.')
            else:
                raise NotImplementedError('factorisation of modulus not implemented yet')
        nperiod = self.exponent * self.d - 1
        # x*(a*b + 1 - b - a) / gcd
        raise NotImplementedError('todo finish this')

    def _encrypt(self, msg):
        msg = Blocks.to_padded_message(msg, self.block_size)
        chunk_size = self.block_size / 8
        assert len(msg)%chunk_size == 0, len(msg) % 8
        res = ''
        state_period = 2**self.block_size
        state = self.INITIAL_STATE % state_period
        for pos in xrange(0, len(msg), chunk_size):
            block = msg[pos:pos+chunk_size]
            num = Blocks.block_to_num(block)
            enc_num = self._encode_number(num) ^ state
            bl = Blocks.num_to_block(enc_num, self.block_size+8)
            state = self.hash_from_msg(block+str(state)) % state_period
            res += bl
        return res

    def _decrypt(self, msg):
        assert self.d is not None, 'private key missing!'
        chunk_size = self.block_size / 8 + 1
        max_encodable_num = 2**self.block_size
        assert len(msg) % chunk_size == 0, 'Invalid length of the encrypted message %d!' % len(msg)
        res = ''
        state_period = 2**self.block_size
        state = self.INITIAL_STATE % state_period
        for pos in xrange(0, len(msg), chunk_size):
            block = msg[pos:pos+chunk_size]
            num = Blocks.block_to_num(block) ^ state
            dec_num = self._decode_number(num)
            assert dec_num < max_encodable_num, 'Invalid d?'
            bl = Blocks.num_to_block(dec_num, self.block_size)
            state = self.hash_from_msg(bl+str(state)) % state_period
            res += bl
        return Blocks.from_padded_message(res, self.block_size)

    def _decode_number(self, num):
        return pow(num, self.d, self.modulus)

    def _encode_number(self, num):
        return pow(num, self.exponent, self.modulus)

    @staticmethod
    def hash_from_msg(msg):
        return long(sha256(msg).hexdigest(), 16)

    def encrypt(self, msg):
        return self._encrypt(self._encrypt(msg)[::-1])

    def decrypt(self, msg):
        return self._decrypt(self._decrypt(msg)[::-1])

    def sign(self, claim):
        if isinstance(claim, basestring):
            claim = Claim(claim)
        claim_hash = self.hash_from_msg(claim.msg) % self.modulus
        claim.exponent = self.exponent
        claim.modulus = self.modulus
        claim.signature = self._decode_number(claim_hash)
        return claim

    def verify(self, claim):
        claim_hash = self.hash_from_msg(claim.msg) % self.modulus
        return claim_hash == self._encode_number(claim.signature)


class Claim:
    def __init__(self, msg):
        self.msg = msg
        self.exponent = 0
        self.modulus = 0
        self.signature = 0

    def to_string(self):
        return ';'.join((
            self.msg.encode('hex'),
            hex(self.exponent)[2:],
            hex(self.modulus)[2:],
            hex(self.signature)[2:],
        ))

    @classmethod
    def from_string(cls, string):
        msg, e, m, s = string.split(';')
        cand = Claim(msg.decode('hex'))
        m = long(m, 16)
        if not m:
            return cand
        cand.modulus = m
        cand.exponent = long(e, 16)
        cand.signature = long(s, 16)
        return cand

    def verify(self):
        if not self.modulus:
            return False
        if not self.signature or not self.exponent:
            return False
        rsa = RSA(self.exponent, self.modulus)
        return rsa.verify(self)





class Blocks:
    @classmethod
    def to_padded_message(cls, msg, block_size):
        assert block_size % 8==0
        initial_len = len(msg)
        assert initial_len < 2**block_size, 'Block size to small to encode message this long'
        rem = initial_len % (block_size / 8)
        if rem != 0:
            msg = '?' * (block_size / 8 - rem) + msg
        return cls.num_to_block(initial_len, block_size) + msg

    @classmethod
    def from_padded_message(cls, padded_message, block_size):
        assert block_size % 8==0
        initial_len = cls.block_to_num(padded_message[:block_size/8])
        return padded_message[-initial_len:]

    @staticmethod
    def num_to_block(num, block_size):
        assert block_size % 8==0
        res = ''
        for _ in xrange(block_size/8):
            res = chr(num % 256) + res
            num /= 256
        assert num == 0 and len(res)== block_size/8
        return res

    @staticmethod
    def block_to_num(block):
        num = 0
        for e in block:
            num *= 256
            num += ord(e)
        return num


if __name__ == '__main__':
    a = RSA.get_random_rsa()
    assert Blocks.from_padded_message(Blocks.to_padded_message('hello', 512), 512) == 'hello'

    import time
    t = time.time()
    s = 'rsa is cool - '*10
    x = a.encrypt(s)
    print x
    assert x!=s
    print len(s), len(x)
    print 'DECODING'
    dec = a.decrypt(x)
    print dec
    assert dec == s
    print time.time() - t

    claim = a.sign('Piter is the best!')
    print claim.signature
    assert claim.verify()
    print claim.verify()
    claim_str = claim.to_string()
    print claim_str
    claim_recovered = Claim.from_string(claim_str)
    assert claim_recovered.verify()
    claim.signature += 1
    assert not claim.verify()

