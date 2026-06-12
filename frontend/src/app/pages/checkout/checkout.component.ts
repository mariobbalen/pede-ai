import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar } from '@angular/material/snack-bar';

import { CartService } from '../../services/cart.service';
import { IdentityService } from '../../services/identity.service';
import { OrderService } from '../../services/order.service';
import { CartSummaryComponent } from '../../components/cart-summary/cart-summary.component';
import { AddressPickerComponent, SelectedAddress } from '../../components/address-picker/address-picker.component';
import { CreateOrderPayload } from '../../models/order.model';

@Component({
  selector: 'app-checkout',
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    CartSummaryComponent,
    AddressPickerComponent,
  ],
  templateUrl: './checkout.component.html',
  styleUrl: './checkout.component.scss',
})
export class CheckoutComponent implements OnInit {
  customerName = '';
  selectedAddress: SelectedAddress | null = null;
  submitting = false;

  constructor(
    private router: Router,
    private cartService: CartService,
    private identityService: IdentityService,
    private orderService: OrderService,
    private snackBar: MatSnackBar
  ) {}

  get cart() {
    return this.cartService.snapshot;
  }

  get cartTotal(): number {
    return this.cartService.getTotal();
  }

  ngOnInit(): void {
    if (this.cart.items.length === 0) {
      this.router.navigate(['/restaurants']);
      return;
    }
    this.customerName = this.identityService.getCustomerName() ?? '';
  }

  onAddressSelected(address: SelectedAddress): void {
    this.selectedAddress = address;
  }

  canSubmit(): boolean {
    return !this.submitting && this.customerName.trim().length > 0 && this.selectedAddress !== null;
  }

  submitOrder(): void {
    if (!this.canSubmit() || !this.cart.restaurantId || !this.selectedAddress) {
      return;
    }

    this.submitting = true;
    this.identityService.setCustomerName(this.customerName.trim());

    const payload: CreateOrderPayload = {
      restaurant: this.cart.restaurantId,
      items: this.cart.items.map((item) => ({
        menu_item_id: item.menu_item_id,
        quantity: item.quantity,
      })),
      address: this.selectedAddress.address,
      latitude: Number(this.selectedAddress.lat.toFixed(6)),
      longitude: Number(this.selectedAddress.lng.toFixed(6)),
      customer_name: this.customerName.trim(),
    };

    this.orderService.create(payload).subscribe({
      next: (order) => {
        this.cartService.clear();
        this.identityService.addOrderToHistory(order.id);
        this.router.navigate(['/orders', order.id]);
      },
      error: () => {
        this.submitting = false;
        this.snackBar.open('Não foi possível enviar o pedido. Tente novamente.', 'Fechar', { duration: 5000 });
      },
    });
  }
}
