import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { Subject, interval } from 'rxjs';
import { startWith, switchMap, takeUntil } from 'rxjs/operators';

import { OrderService } from '../../services/order.service';
import { Order } from '../../models/order.model';
import { StatusStepperComponent } from '../../components/status-stepper/status-stepper.component';

const POLL_INTERVAL_MS = 5000;

@Component({
  selector: 'app-order-tracking',
  imports: [CommonModule, MatButtonModule, MatCardModule, StatusStepperComponent],
  templateUrl: './order-tracking.component.html',
  styleUrl: './order-tracking.component.scss',
})
export class OrderTrackingComponent implements OnInit, OnDestroy {
  order: Order | null = null;
  loading = true;
  confirming = false;

  private destroy$ = new Subject<void>();

  constructor(private route: ActivatedRoute, private orderService: OrderService) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id')!;

    interval(POLL_INTERVAL_MS)
      .pipe(
        startWith(0),
        switchMap(() => this.orderService.get(id)),
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: (order) => {
          this.order = order;
          this.loading = false;
          if (order.status === 'delivered') {
            this.destroy$.next();
          }
        },
        error: () => {
          this.loading = false;
        },
      });
  }

  confirmDelivery(): void {
    if (!this.order) {
      return;
    }
    this.confirming = true;
    this.orderService.confirmDelivery(this.order.id).subscribe({
      next: (order) => {
        this.order = order;
        this.confirming = false;
      },
      error: () => {
        this.confirming = false;
      },
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
