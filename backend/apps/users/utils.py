from apps.users.models import User


def deposit_percent(user: User):
    match user.deposit_commission_status:
        case User.DepositCommissionStatus.PRE_STANDARD:
            return 15
        case User.DepositCommissionStatus.STANDARD:
            return 10
        case User.DepositCommissionStatus.VIP:
            return 5
        case User.DepositCommissionStatus.ADMIN:
            return 1
        case User.DepositCommissionStatus.SUPER_USER:
            return 0


def withdraw_percent(user: User):
    match user.withdraw_commission_status:
        case User.WithdrawCommissionStatus.PRE_STANDARD:
            return 10
        case User.WithdrawCommissionStatus.STANDARD:
            return 8
        case User.WithdrawCommissionStatus.VIP:
            return 3
        case User.WithdrawCommissionStatus.ADMIN:
            return 1
        case User.WithdrawCommissionStatus.SUPER_USER:
            return 0
