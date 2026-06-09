from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from shared.permissions import IsOwnerOrAdmin
from .models import Payment
from .serializers import PaymentSerializer
from notifications.utils import send_notification


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.user_role == "admin":
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)

    @action(detail=True, methods=["post"])
    def confirm_payment(self, request, pk=None):
        payment = self.get_object()
        if payment.status != "pending":
            return Response({"error": "Payment already processed"}, status=status.HTTP_400_BAD_REQUEST)

        # Simulate success
        payment.status = "completed"
        payment.transaction_id = "simulated_txn_id"
        payment.save()

        # Update order status to paid
        payment.order.status = "paid"
        payment.order.save()

        # --- Send notification to the user who placed the order ---
        send_notification(
            user=payment.order.user,
            message=f"Your payment for order #{payment.order.id} has been confirmed.",
            notification_type="payment_success"
        )

        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)