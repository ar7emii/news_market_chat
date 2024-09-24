from Clonliner.models import Chat


def unseen_messages_count(request):
    if request.user.is_authenticated:
        unseen_messages_count_all = Chat.objects.filter(users=request.user, messages__status='unseen')
        unseen_messages_sent_by_me = Chat.objects.filter(users=request.user, messages__status='unseen',
                                                               messages__sender=request.user)

        chats_with_unseen_messages_sent_to_me = unseen_messages_count_all.exclude(
            id__in=unseen_messages_sent_by_me.values('id')).distinct()
        count_chats_with_unseen_messages_sent_to_me = chats_with_unseen_messages_sent_to_me.count()
    else:
        chats_with_unseen_messages_sent_to_me = None
        count_chats_with_unseen_messages_sent_to_me = 0

    return {
        'count_chats_with_unseen_messages_sent_to_me': count_chats_with_unseen_messages_sent_to_me,
        'chats_with_unseen_messages_sent_to_me': chats_with_unseen_messages_sent_to_me
    }
