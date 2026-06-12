import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

import { MenuItem } from '../models/restaurant.model';

export interface CartLineItem {
  menu_item_id: string;
  name: string;
  price: string;
  quantity: number;
}

export interface CartState {
  restaurantId: string | null;
  items: CartLineItem[];
}

const STORAGE_KEY = 'pedeai_cart';

@Injectable({ providedIn: 'root' })
export class CartService {
  private state$ = new BehaviorSubject<CartState>(this.loadFromStorage());

  readonly cart$: Observable<CartState> = this.state$.asObservable();

  get snapshot(): CartState {
    return this.state$.value;
  }

  belongsToOtherRestaurant(restaurantId: string): boolean {
    const current = this.state$.value;
    return current.restaurantId !== null && current.restaurantId !== restaurantId && current.items.length > 0;
  }

  addItem(restaurantId: string, menuItem: MenuItem, quantity = 1): void {
    const current = this.state$.value;
    const items = current.restaurantId === restaurantId ? [...current.items] : [];

    const existing = items.find((item) => item.menu_item_id === menuItem.id);
    if (existing) {
      existing.quantity += quantity;
    } else {
      items.push({
        menu_item_id: menuItem.id,
        name: menuItem.name,
        price: menuItem.price,
        quantity,
      });
    }

    this.setState({ restaurantId, items });
  }

  updateQuantity(menuItemId: string, quantity: number): void {
    const current = this.state$.value;
    if (quantity <= 0) {
      this.removeItem(menuItemId);
      return;
    }
    const items = current.items.map((item) =>
      item.menu_item_id === menuItemId ? { ...item, quantity } : item
    );
    this.setState({ ...current, items });
  }

  removeItem(menuItemId: string): void {
    const current = this.state$.value;
    const items = current.items.filter((item) => item.menu_item_id !== menuItemId);
    this.setState({
      restaurantId: items.length > 0 ? current.restaurantId : null,
      items,
    });
  }

  clear(): void {
    this.setState({ restaurantId: null, items: [] });
  }

  getTotal(): number {
    return this.state$.value.items.reduce(
      (total, item) => total + parseFloat(item.price) * item.quantity,
      0
    );
  }

  private setState(state: CartState): void {
    this.state$.next(state);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  private loadFromStorage(): CartState {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return { restaurantId: null, items: [] };
    }
    try {
      return JSON.parse(raw) as CartState;
    } catch {
      return { restaurantId: null, items: [] };
    }
  }
}
