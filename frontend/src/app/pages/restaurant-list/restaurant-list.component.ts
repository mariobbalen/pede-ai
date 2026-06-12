import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';

import { RestaurantService } from '../../services/restaurant.service';
import { RestaurantSummary } from '../../models/restaurant.model';

@Component({
  selector: 'app-restaurant-list',
  imports: [CommonModule, RouterLink, MatCardModule, MatButtonModule],
  templateUrl: './restaurant-list.component.html',
  styleUrl: './restaurant-list.component.scss',
})
export class RestaurantListComponent implements OnInit {
  restaurants: RestaurantSummary[] = [];
  loading = true;

  constructor(private restaurantService: RestaurantService) {}

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
}
