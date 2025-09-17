### `backend/app/debt.py`

from typing import List, Dict
from .schemas import Settlement

# Greedy min-cash-flow algorithm: not always globally minimal edges, but works well and is simple.

def minimize_cash_flow(balances: Dict[int, float]) -> List[Settlement]:
    debtors = []  # (user_id, amount_owed)
    creditors = []  # (user_id, amount_due)

    for uid, net in balances.items():
        if round(net, 2) < 0:
            debtors.append([uid, round(-net, 2)])
        elif round(net, 2) > 0:
            creditors.append([uid, round(net, 2)])

    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    settlements: List[Settlement] = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        d_uid, d_amt = debtors[i]
        c_uid, c_amt = creditors[j]
        pay = round(min(d_amt, c_amt), 2)
        if pay > 0:
            settlements.append(Settlement(from_user=d_uid, to_user=c_uid, amount=pay))
        debtors[i][1] = round(d_amt - pay, 2)
        creditors[j][1] = round(c_amt - pay, 2)
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1
    return settlements
