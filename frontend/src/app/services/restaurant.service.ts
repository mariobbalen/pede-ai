import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { PaginatedResponse } from '../models/paginated-response.model';
import { RestaurantDetail, RestaurantSummary } from '../models/restaurant.model';

@Injectable({ providedIn: 'root' })
export class RestaurantService {
  constructor(private http: HttpClient) {}

  list(): Observable<PaginatedResponse<RestaurantSummary>> {
    return this.http.get<PaginatedResponse<RestaurantSummary>>(`${environment.apiBaseUrl}/restaurants/`);
  }

  get(id: string): Observable<RestaurantDetail> {
    return this.http.get<RestaurantDetail>(`${environment.apiBaseUrl}/restaurants/${id}/`);
  }
}
