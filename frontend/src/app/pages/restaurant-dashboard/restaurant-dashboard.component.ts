import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { Subject, interval } from 'rxjs';
import { startWith, switchMap, takeUntil } from 'rxjs/operators';

import { OrderService } from '../../services/order.service';
import { RestaurantService } from '../../services/restaurant.service';
import { IdentityService } from '../../services/identity.service';
import { ADVANCE_BUTTON_LABELS, Order, OrderStatus, STATUS_FLOW, STATUS_MESSAGES } from '../../models/order.model';

const POLL_INTERVAL_MS = 5000;

@Component({
  selector: 'app-restaurant-dashboard',
  imports: [CommonModule, MatCardModule, MatButtonModule],
  templateUrl: './restaurant-dashboard.component.html',
  styleUrl: './restaurant-dashboard.component.scss',
})
export class RestaurantDashboardComponent implements OnInit, OnDestroy {
  restaurantName = '';
  orders: Order[] = [];
  loading = true;
  advancingOrderId: string | null = null;

  private destroy$ = new Subject<void>();

  constructor(
    private router: Router,
    private orderService: OrderService,
    private restaurantService: RestaurantService,
    private identityService: IdentityService
  ) {}

  ngOnInit(): void {
    const restaurantId = this.identityService.getSelectedRestaurantId();
    if (!restaurantId) {
      this.router.navigate(['/restaurant-login']);
      return;
    }

    this.restaurantService.get(restaurantId).subscribe({
      next: (restaurant) => (this.restaurantName = restaurant.name),
    });

    interval(POLL_INTERVAL_MS)
      .pipe(
        startWith(0),
        switchMap(() => this.orderService.listByRestaurant(restaurantId)),
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: (response) => {
          this.orders = response.results;
          this.loading = false;
        },
        error: () => {
          this.loading = false;
        },
      });
  }

  statusMessage(status: OrderStatus): string {
    return STATUS_MESSAGES[status];
  }

  advanceLabel(order: Order): string | null {
    const currentIndex = STATUS_FLOW.indexOf(order.status);
    if (currentIndex < 0 || currentIndex >= STATUS_FLOW.length - 1) {
      return null;
    }
    const next = STATUS_FLOW[currentIndex + 1];
    return ADVANCE_BUTTON_LABELS[next] ?? null;
  }

  advance(order: Order): void {
    this.advancingOrderId = order.id;
    this.orderService.advance(order.id).subscribe({
      next: (updated) => {
        this.orders = this.orders.map((o) => (o.id === updated.id ? updated : o));
        this.advancingOrderId = null;
      },
      error: () => {
        this.advancingOrderId = null;
      },
    });
  }

  changeRestaurant(): void {
    this.identityService.clearSelectedRestaurant();
    this.router.navigate(['/restaurant-login']);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
