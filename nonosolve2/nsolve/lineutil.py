def generate_pstate_combi(pstate_matrix):
    new_pstates = {}
    for i, pstates in enumerate(pstate_matrix):
        if i > 0:
            left_pstate_combis = generate_pstate_combi(pstate_matrix[0:i])
        else:
            left_pstate_combis = {tuple(): []}
        if i < len(pstate_matrix) - 1:
            right_pstate_combis = generate_pstate_combi(pstate_matrix[i+1:])
        else:
            right_pstate_combis = {tuple(): []}
        for pstate in pstates:
            for l, lc in left_pstate_combis.items():
                for r, rc in right_pstate_combis.items():
                    new_pstate = tuple(list(l) + list(pstate) + list(r))
                    new_pstates[new_pstate] = lc + [pstate] + rc
    return new_pstates