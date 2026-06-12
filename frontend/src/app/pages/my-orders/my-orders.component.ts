import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { Subject, forkJoin, interval, of } from 'rxjs';
import { catchError, startWith, switchMap, takeUntil } from 'rxjs/operators';

import { OrderService } from '../../services/order.service';
import { IdentityService } from '../../services/identity.service';
import { Order, STATUS_MESSAGES } from '../../models/order.model';

const POLL_INTERVAL_MS = 10000;

@Component({
  selector: 'app-my-orders',
  imports: [CommonModule, RouterLink, MatCardModule, MatButtonModule],
  templateUrl: './my-orders.component.html',
  styleUrl: './my-orders.component.scss',
})
export class MyOrdersComponent implements OnInit, OnDestroy {
  orders: Order[] = [];
  loading = true;
  confirmingOrderId: string | null = null;

  private destroy$ = new Subject<void>();

  constructor(private orderService: OrderService, private identityService: IdentityService) {}

  ngOnInit(): void {
    const orderIds = this.identityService.getOrderHistory();

    if (orderIds.length === 0) {
      this.loading = false;
      return;
    }

    interval(POLL_INTERVAL_MS)
      .pipe(
        startWith(0),
        switchMap(() =>
          forkJoin(orderIds.map((id) => this.orderService.get(id).pipe(catchError(() => of(null)))))
        ),
        takeUntil(this.destroy$)
      )
      .subscribe((orders) => {
        this.orders = orders.filter((order): order is Order => order !== null);
        this.loading = false;
      });
  }

  statusLabel(order: Order): string {
    return STATUS_MESSAGES[order.status];
  }

  confirmDelivery(order: Order): void {
    this.confirmingOrderId = order.id;
    this.orderService.confirmDelivery(order.id).subscribe({
      next: (updated) => {
        this.orders = this.orders.map((o) => (o.id === updated.id ? updated : o));
        this.confirmingOrderId = null;
      },
      error: () => {
        this.confirmingOrderId = null;
      },
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
