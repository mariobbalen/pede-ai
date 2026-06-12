import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';

import { RestaurantService } from '../../services/restaurant.service';
import { IdentityService } from '../../services/identity.service';
import { RestaurantSummary } from '../../models/restaurant.model';

@Component({
  selector: 'app-restaurant-login',
  imports: [CommonModule, MatListModule, MatIconModule],
  templateUrl: './restaurant-login.component.html',
  styleUrl: './restaurant-login.component.scss',
})
export class RestaurantLoginComponent implements OnInit {
  restaurants: RestaurantSummary[] = [];
  loading = true;

  constructor(
    private restaurantService: RestaurantService,
    private identityService: IdentityService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.restaurantService.list().subscribe({
      next: (response) => {
        this.restaurants = response.results;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  selectRestaurant(restaurant: RestaurantSummary): void {
    this.identityService.setSelectedRestaurantId(restaurant.id);
    this.router.navigate(['/dashboard']);
  }
}
