from rope import Node

def simon_rope() -> Node:
    A, B, C, D, E, F, G, H, J, K, M, N = Node(), Node(), Node(), Node(), Node(), Node(), Node(), Node(), Node(), Node(), Node(), Node()
    A.set_left(B)
    B.set_left(C)
    C.set_left(E)
    E.set_value("Hello ")
    C.set_right(F)
    F.set_value("my ")
    B.set_right(D)
    D.set_left(G)
    G.set_left(J)
    J.set_value("na")
    G.set_right(K)
    K.set_value("me i")
    D.set_right(H)
    H.set_left(M)
    M.set_value("s")
    H.set_right(N)
    N.set_value(" Simon")

    return A

def smol():
    A, B = Node(), Node()
    A.set_left(B)
    B.set_value('abuba')
    
    return A

simmy = simon_rope()
print(simmy.is_balanced)

for i in range(23):
    a, b = simmy.split(i)
    if a: a = a.rebalance()
    if b: b = b.rebalance()
    print('' if not a else a.collect(), '+', '' if not b else b.collect())
    print(True if not a else a.is_balanced, True if not b else b.is_balanced)