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

simmy = simon_rope()
print(simmy[-1])