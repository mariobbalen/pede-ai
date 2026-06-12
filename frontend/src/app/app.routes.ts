import { Routes } from '@angular/router';

import { RestaurantListComponent } from './pages/restaurant-list/restaurant-list.component';
import { RestaurantDetailComponent } from './pages/restaurant-detail/restaurant-detail.component';
import { CheckoutComponent } from './pages/checkout/checkout.component';
import { OrderTrackingComponent } from './pages/order-tracking/order-tracking.component';
import { MyOrdersComponent } from './pages/my-orders/my-orders.component';
import { RestaurantLoginComponent } from './pages/restaurant-login/restaurant-login.component';
import { RestaurantDashboardComponent } from './pages/restaurant-dashboard/restaurant-dashboard.component';

export const routes: Routes = [
  { path: '', redirectTo: 'restaurants', pathMatch: 'full' },
  { path: 'restaurants', component: RestaurantListComponent },
  { path: 'restaurants/:id', component: RestaurantDetailComponent },
  { path: 'checkout', component: CheckoutComponent },
  { path: 'orders/:id', component: OrderTrackingComponent },
  { path: 'my-orders', component: MyOrdersComponent },
  { path: 'restaurant-login', component: RestaurantLoginComponent },
  { path: 'dashboard', component: RestaurantDashboardComponent },
  { path: '**', redirectTo: 'restaurants' },
];
