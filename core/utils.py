from core.models import AssociationFee, SkillAquisition

# def get_payment_model_instance(name):
#     # This logic can be refined based on what you're storing in `name`
#     try:
#         return AssociationFee.objects.get(session=name)
#     except AssociationFee.DoesNotExist:
#         pass
#     try:
#         return SkillAquisition.objects.get(skill_type=name)
#     except SkillAquisition.DoesNotExist:
#         pass
#     return None


def get_payment_model_instance(payment_type, value):
    if payment_type == "fee":
        return AssociationFee.objects.filter(session=value).first()
    elif payment_type == "skill":
        return SkillAquisition.objects.filter(skill_type=value).first()
    return None