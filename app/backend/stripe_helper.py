"""
Stripe Helper - Native Stripe implementation to replace emergentintegrations
Supports both legacy (amount/currency) and new (line_items) formats
"""
import stripe
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class CheckoutSessionRequest:
    """Flexible checkout request supporting multiple parameter formats."""
    success_url: str
    cancel_url: str
    # New format
    line_items: Optional[List[Dict[str, Any]]] = None
    mode: str = "payment"
    # Legacy format (from emergentintegrations)
    amount: Optional[float] = None
    currency: str = "chf"
    quantity: int = 1
    product_name: Optional[str] = None
    # Common
    metadata: Optional[Dict[str, str]] = None
    customer_email: Optional[str] = None


@dataclass
class CheckoutSessionResponse:
    """Response from creating a checkout session."""
    id: str
    url: str
    status: str
    payment_status: str
    # Aliases for compatibility
    session_id: str = ""
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = self.id


@dataclass
class CheckoutStatusResponse:
    """Response from checking session status."""
    id: str
    status: str
    payment_status: str
    amount_total: int
    currency: str


class StripeCheckout:
    """Stripe checkout helper class."""
    
    def __init__(self, api_key: str, webhook_url: str = ""):
        self.api_key = api_key
        self.webhook_url = webhook_url
        stripe.api_key = api_key
    
    def _build_line_items(self, request: CheckoutSessionRequest) -> List[Dict]:
        """Build line_items from either format."""
        # If line_items provided directly, use them
        if request.line_items:
            return request.line_items
        
        # Build from legacy amount/currency format
        if request.amount is not None:
            product_name = request.product_name or "Paiement Titelli"
            if request.metadata and request.metadata.get("product_name"):
                product_name = request.metadata["product_name"]
            
            return [{
                "price_data": {
                    "currency": request.currency,
                    "product_data": {"name": product_name},
                    "unit_amount": int(request.amount * 100)  # Convert to cents
                },
                "quantity": request.quantity
            }]
        
        raise ValueError("Either line_items or amount must be provided")
    
    async def create_session(self, request: CheckoutSessionRequest) -> CheckoutSessionResponse:
        """Create a Stripe checkout session (async)."""
        return self._create_session_internal(request)
    
    async def create_checkout_session(self, request: CheckoutSessionRequest) -> CheckoutSessionResponse:
        """Alias for create_session for compatibility."""
        return self._create_session_internal(request)
    
    def create_session_sync(self, request: CheckoutSessionRequest) -> CheckoutSessionResponse:
        """Create a Stripe checkout session (sync)."""
        return self._create_session_internal(request)
    
    def _create_session_internal(self, request: CheckoutSessionRequest) -> CheckoutSessionResponse:
        """Internal method to create checkout session."""
        try:
            line_items = self._build_line_items(request)
            
            session_params = {
                "line_items": line_items,
                "mode": request.mode,
                "success_url": request.success_url,
                "cancel_url": request.cancel_url,
            }
            
            if request.metadata:
                # Filter out non-string values for Stripe metadata
                clean_metadata = {k: str(v) for k, v in request.metadata.items() if v is not None}
                session_params["metadata"] = clean_metadata
            
            if request.customer_email:
                session_params["customer_email"] = request.customer_email
            
            session = stripe.checkout.Session.create(**session_params)
            
            return CheckoutSessionResponse(
                id=session.id,
                url=session.url,
                status=session.status or "open",
                payment_status=session.payment_status or "unpaid",
                session_id=session.id
            )
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
        except Exception as e:
            raise Exception(f"Stripe session creation failed: {str(e)}")
    
    async def get_session_status(self, session_id: str) -> CheckoutStatusResponse:
        """Get the status of a checkout session."""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            return CheckoutStatusResponse(
                id=session.id,
                status=session.status or "unknown",
                payment_status=session.payment_status or "unknown",
                amount_total=session.amount_total or 0,
                currency=session.currency or "chf"
            )
        except Exception as e:
            raise Exception(f"Failed to get session status: {str(e)}")
