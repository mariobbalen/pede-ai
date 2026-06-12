import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { CreateOrderPayload, Order } from '../models/order.model';
import { PaginatedResponse } from '../models/paginated-response.model';

@Injectable({ providedIn: 'root' })
export class OrderService {
  constructor(private http: HttpClient) {}

  create(payload: CreateOrderPayload): Observable<Order> {
    return this.http.post<Order>(`${environment.apiBaseUrl}/orders/`, payload);
  }

  get(id: string): Observable<Order> {
    return this.http.get<Order>(`${environment.apiBaseUrl}/orders/${id}/`);
  }

  listByRestaurant(restaurantId: string): Observable<PaginatedResponse<Order>> {
    return this.http.get<PaginatedResponse<Order>>(`${environment.apiBaseUrl}/orders/`, {
      params: { restaurant: restaurantId },
    });
  }

  advance(id: string): Observable<Order> {
    return this.http.post<Order>(`${environment.apiBaseUrl}/orders/${id}/advance/`, {});
  }

  confirmDelivery(id: string): Observable<Order> {
    return this.http.post<Order>(`${environment.apiBaseUrl}/orders/${id}/confirm-delivery/`, {});
  }
}
