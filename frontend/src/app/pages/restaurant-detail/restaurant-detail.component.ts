import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog } from '@angular/material/dialog';
import { map } from 'rxjs';

import { RestaurantService } from '../../services/restaurant.service';
import { CartLineItem, CartService } from '../../services/cart.service';
import { RestaurantDetail, MenuItem } from '../../models/restaurant.model';
import { CartSummaryComponent } from '../../components/cart-summary/cart-summary.component';
import { ConfirmDialogComponent } from '../../components/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-restaurant-detail',
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, CartSummaryComponent],
  templateUrl: './restaurant-detail.component.html',
  styleUrl: './restaurant-detail.component.scss',
})
export class RestaurantDetailComponent implements OnInit {
  restaurant: RestaurantDetail | null = null;
  loading = true;
  quantities: Record<string, number> = {};

  cart$;
  total$;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private restaurantService: RestaurantService,
    private cartService: CartService,
    private dialog: MatDialog
  ) {
    this.cart$ = this.cartService.cart$;
    this.total$ = this.cartService.cart$.pipe(map(() => this.cartService.getTotal()));
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id')!;
    this.restaurantService.get(id).subscribe({
      next: (restaurant) => {
        this.restaurant = restaurant;
        for (const item of restaurant.menu_items) {
          this.quantities[item.id] = 1;
        }
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  increaseQuantity(itemId: string): void {
    this.quantities[itemId] = (this.quantities[itemId] ?? 1) + 1;
  }

  decreaseQuantity(itemId: string): void {
    const current = this.quantities[itemId] ?? 1;
    this.quantities[itemId] = Math.max(1, current - 1);
  }

  addToCart(item: MenuItem): void {
    if (!this.restaurant) {
      return;
    }
    const quantity = this.quantities[item.id] ?? 1;
    const restaurantId = this.restaurant.id;

    if (this.cartService.belongsToOtherRestaurant(restaurantId)) {
      const dialogRef = this.dialog.open(ConfirmDialogComponent, {
        data: {
          title: 'Trocar de restaurante?',
          message:
            'Seu carrinho tem itens de outro restaurante. Deseja limpar o carrinho e continuar com este pedido?',
          confirmLabel: 'Limpar e continuar',
        },
      });
      dialogRef.afterClosed().subscribe((confirmed) => {
        if (confirmed) {
          this.cartService.clear();
          this.cartService.addItem(restaurantId, item, quantity);
        }
      });
      return;
    }

    this.cartService.addItem(restaurantId, item, quantity);
  }

  goToCheckout(): void {
    this.router.navigate(['/checkout']);
  }

  onCartIncrease(item: CartLineItem): void {
    this.cartService.updateQuantity(item.menu_item_id, item.quantity + 1);
  }

  onCartDecrease(item: CartLineItem): void {
    this.cartService.updateQuantity(item.menu_item_id, item.quantity - 1);
  }

  onCartRemove(item: CartLineItem): void {
    this.cartService.removeItem(item.menu_item_id);
  }
}
