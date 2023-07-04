from apps.users.models import User


def deposit_percent(user: User):
    match user.withdraw_commission_percent:
        case User.WithdrawCommissionPercent.PRE_STANDARD:
            return 15
        case User.WithdrawCommissionPercent.STANDARD:
            return 10
        case User.WithdrawCommissionPercent.VIP:
            return 5
        case User.WithdrawCommissionPercent.ADMIN:
            return 1
        case User.WithdrawCommissionPercent.SUPER_USER:
            return 0


def withdraw_percent(user: User):
    match user.withdraw_commission_percent:
        case User.WithdrawCommissionPercent.PRE_STANDARD:
            return 10
        case User.WithdrawCommissionPercent.STANDARD:
            return 8
        case User.WithdrawCommissionPercent.VIP:
            return 3
        case User.WithdrawCommissionPercent.ADMIN:
            return 1
        case User.WithdrawCommissionPercent.SUPER_USER:
            return 0
