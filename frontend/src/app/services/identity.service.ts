import { Injectable } from '@angular/core';

const CUSTOMER_NAME_KEY = 'pedeai_customer_name';
const SELECTED_RESTAURANT_KEY = 'pedeai_selected_restaurant_id';
const ORDER_HISTORY_KEY = 'pedeai_order_history';
const MAX_ORDER_HISTORY = 20;

@Injectable({ providedIn: 'root' })
export class IdentityService {
  getCustomerName(): string | null {
    return localStorage.getItem(CUSTOMER_NAME_KEY);
  }

  setCustomerName(name: string): void {
    localStorage.setItem(CUSTOMER_NAME_KEY, name);
  }

  getSelectedRestaurantId(): string | null {
    return localStorage.getItem(SELECTED_RESTAURANT_KEY);
  }

  setSelectedRestaurantId(id: string): void {
    localStorage.setItem(SELECTED_RESTAURANT_KEY, id);
  }

  clearSelectedRestaurant(): void {
    localStorage.removeItem(SELECTED_RESTAURANT_KEY);
  }

  getOrderHistory(): string[] {
    const raw = localStorage.getItem(ORDER_HISTORY_KEY);
    if (!raw) {
      return [];
    }
    try {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  addOrderToHistory(orderId: string): void {
    const history = [orderId, ...this.getOrderHistory().filter((id) => id !== orderId)];
    localStorage.setItem(ORDER_HISTORY_KEY, JSON.stringify(history.slice(0, MAX_ORDER_HISTORY)));
  }
}
