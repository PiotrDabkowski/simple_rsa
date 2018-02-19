import math
import random
from profilehooks import profile


def get_primes(n):
    """Returns all the primes until n"""
    # Entry at index i corresponds to 3+2i
    if n <= 2:
        return []
    cands = (n / 2 - 1) * [1]
    for nonzero in xrange(0, int(n ** 0.5) / 2):
        if not cands[nonzero]:
            continue
        value = 3 + 2 * nonzero
        for e in xrange(nonzero + value, len(cands), value):
            cands[e] = 0
    return [2] + [3 + 2 * i for i, e in enumerate(cands) if e]


def check_if_perfect_power(n):
    """Check if a number can be written as a^b where a and b are integers greater than 1. Returns (a, b) if yes."""
    lim_b = int(1.01*(math.log(n)/math.log(2)) + 1)
    possible_b = get_primes(lim_b)
    for b in possible_b:
        approx_a = n**(1./b)
        a_low = int(0.99*approx_a)
        a_high = int(1.01*approx_a) + 1
        # now perform binary search to find a...
        while a_low < a_high:
            a = (a_low + a_high) / 2
            res = a**b
            if res == n:
                return (a, b)
            elif res < n:
                a_low = a + 1
            else:
                a_high = a
    return False



def get_sd(x):
    """Returns (s: int, d: int) for which x = d*2^s """
    if not x:
        return 0, 0
    s = 0
    while 1:
        if x % 2 == 0:
            x /= 2
            s += 1
        else:
            return s, x


def fast_pow_mod(x, p, m):
    """Quickly calculates x**p % m, of course you will see the benefits for larger p"""
    assert m > 1 and p >= 0
    if x < 2:
        return x
    r = 1
    h = x % m
    while 1:
        if p % 2:
            r = (r * h) % m
            if p == 1:
                return r
        h = (h * h) % m
        p /= 2


def is_prime(x, num_check=None):
    # if num_check is None then will check all possibilities, otherwise num_check but may give false positives
    assert isinstance(x, (long, int))
    if x < 2:
        return False
    if x==2:
        return True
    s, d  = get_sd(x - 1)
    if not s:
        return False  # divisible by 2!
    log2x = int(math.ceil((math.log(x) / math.log(2))))
    rm1 = x-1
    th = min(x, 2*log2x*log2x+1)
    for a in xrange(2, th if num_check is None else num_check+2):
        if num_check is not None:
            a = int(random.random()*(th-5))+2
        if pow(a, d, x) != 1:
            ex = d
            for r in xrange(0, s):
                if pow(a, ex, x) == rm1:
                    break
                ex *= 2
            else:
                return False
    return True



def is_prime_fast(x, TEST_PRIMES=get_primes(10000)):
    """Faster but may give false positives"""
    if x<2:
        return False
    for t in TEST_PRIMES:
        if t==x:
            return True
        if x % t == 0:
            return False
    return True


# def is_prime_aks(x):
#     if check_if_perfect_power(x):
#         return False
#     log2x = int(math.ceil((math.log(x)/math.log(2))))
#     lim_r = log2x*log2x + 2
#     # find the multiplicative order x^k mod r such that r is larger than lim_r
#     r = None
#     for p in get_primes(2*lim_r):
#         if x % p == 0:
#             print p
#             return False
#         if p - 1 > lim_r:
#             r = p
#             break
#     else:
#         raise RuntimeError('could not find r!')
#     print r, x
#     for p in get_primes(min(r+1, int(math.ceil(1.01*x**0.5))+2)):
#         if x % p == 0:
#             print p
#             return False
#
#     for a in xrange(1, int(math.ceil(1.01*r**0.5*log2x))):
#         if (x): pass # ???????? read about polynomials...
#
#     return True


def get_random_number(bits, chunk_bitsize=16):  # assumes random.random is safe enough, check
    chunk = 2**chunk_bitsize
    res = 0
    while bits:
        r = int(random.random()*chunk)
        if bits > chunk_bitsize:
            bits -= chunk_bitsize
        else:
            r %= 2**bits
            bits = 0
        res = res * chunk + r
    return res



def get_random_prime(bits, final_num_checks=None):
    assert isinstance(bits, (int, long))
    min_p = 2 ** (bits-1)
    while 1:
        cand = get_random_number(bits - 1) + min_p
        if is_prime_fast(cand) and is_prime(cand, num_check=2) and is_prime(cand, num_check=final_num_checks):
            return cand


def gcd(a, b):
    if b < a:
        a, b = b, a
    while a:
        a, b = b % a, a
    return b




def solve_mod_problem(a, n, rem):
    """Returns smallest positive b, x such that  a*b == rem + x*n"""
    assert a>0 and n>0 and rem>=0
    d = gcd(a, n)
    if rem==0:
        return n/d, a/d
    old_a = a
    a = a%n
    old_rem = rem
    rem = rem % n

    if rem % d != 0:
        raise ValueError('no such b exists')
    period = a*n/d
    b, _ = _solve_mod_problem(a/d, n/d)
    b = (rem/d*b) % period

    x = b*a/n + old_a/n*b - old_rem/n

    assert old_a * b == old_rem + x * n

    return b, x


def _solve_mod_problem(a, n):
    """Returns b, x such that  a*b == 1 + x*n, not sure if the most optimal, this is what I came up with, logarithmic time"""
    if a == 1:
        return a, 0
    a = a % n
    div = n / a + 1
    off = a - (n % a)
    if off <= a/2: # this guarantees logarithmic time
        partial_b, partial_x = _solve_mod_problem(off, a)
        b = (partial_b * div - partial_x) % (a*n)
    else:
        partial_b, partial_x = _solve_mod_problem(a-off, a)
        b =  -(partial_b * div - partial_b*off/a - 1) % (a*n)
    x = b * a / n
    assert a * b == 1 + x * n
    return b, x


if __name__ == '__main__':
    R = 10000
    primes = set(get_primes(R))
    for e in xrange(R):
        assert is_prime(e) == (e in primes), e