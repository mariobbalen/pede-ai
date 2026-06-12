import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { CartLineItem } from '../../services/cart.service';

@Component({
  selector: 'app-cart-summary',
  imports: [CommonModule, MatButtonModule, MatIconModule],
  templateUrl: './cart-summary.component.html',
  styleUrl: './cart-summary.component.scss',
})
export class CartSummaryComponent {
  @Input() items: CartLineItem[] = [];
  @Input() total = 0;
  @Input() editable = false;

  @Output() increase = new EventEmitter<CartLineItem>();
  @Output() decrease = new EventEmitter<CartLineItem>();
  @Output() remove = new EventEmitter<CartLineItem>();

  lineTotal(item: CartLineItem): number {
    return parseFloat(item.price) * item.quantity;
  }
}
