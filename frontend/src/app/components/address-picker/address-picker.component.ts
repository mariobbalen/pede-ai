import { AfterViewInit, Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import * as L from 'leaflet';

import { AddressSuggestion, reverseGeocode, searchAddress } from '../../utils/nominatim';

// São Paulo, usado quando a geolocalização é negada ou está indisponível.
const FALLBACK_CENTER: L.LatLngTuple = [-23.5505, -46.6333];

const SEARCH_DEBOUNCE_MS = 400;

const markerIcon = L.icon({
  iconUrl: 'leaflet/marker-icon.png',
  iconRetinaUrl: 'leaflet/marker-icon-2x.png',
  shadowUrl: 'leaflet/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

export interface SelectedAddress {
  address: string;
  lat: number;
  lng: number;
}

@Component({
  selector: 'app-address-picker',
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
  ],
  templateUrl: './address-picker.component.html',
  styleUrl: './address-picker.component.scss',
})
export class AddressPickerComponent implements AfterViewInit {
  @ViewChild('mapContainer', { static: true }) mapContainer!: ElementRef<HTMLDivElement>;
  @Output() addressSelected = new EventEmitter<SelectedAddress>();

  currentAddress = '';
  loadingAddress = false;
  locating = false;

  searchQuery = '';
  suggestions: AddressSuggestion[] = [];

  private map!: L.Map;
  private marker!: L.Marker;
  private searchTimeout?: ReturnType<typeof setTimeout>;

  ngAfterViewInit(): void {
    this.initMap(FALLBACK_CENTER);
    this.useCurrentLocation();
  }

  useCurrentLocation(): void {
    if (!navigator.geolocation) {
      this.handlePositionChange(FALLBACK_CENTER[0], FALLBACK_CENTER[1]);
      return;
    }

    this.locating = true;
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const center: L.LatLngTuple = [position.coords.latitude, position.coords.longitude];
        this.locating = false;
        this.setMarkerPosition(center, 16);
      },
      () => {
        this.locating = false;
        this.handlePositionChange(FALLBACK_CENTER[0], FALLBACK_CENTER[1]);
      }
    );
  }

  onSearchInput(): void {
    clearTimeout(this.searchTimeout);

    const query = this.searchQuery.trim();
    if (query.length < 3) {
      this.suggestions = [];
      return;
    }

    this.searchTimeout = setTimeout(() => this.runSearch(query), SEARCH_DEBOUNCE_MS);
  }

  selectSuggestion(suggestion: AddressSuggestion): void {
    const center: L.LatLngTuple = [Number(suggestion.lat), Number(suggestion.lon)];
    this.suggestions = [];
    this.searchQuery = '';
    this.setMarkerPosition(center, 17);
  }

  private async runSearch(query: string): Promise<void> {
    const results = await searchAddress(query);
    if (this.searchQuery.trim() === query) {
      this.suggestions = results;
    }
  }

  private setMarkerPosition(center: L.LatLngTuple, zoom: number): void {
    this.map.setView(center, zoom);
    this.marker.setLatLng(center);
    this.handlePositionChange(center[0], center[1]);
  }

  private initMap(center: L.LatLngTuple): void {
    this.map = L.map(this.mapContainer.nativeElement).setView(center, 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(this.map);

    this.marker = L.marker(center, { icon: markerIcon, draggable: true }).addTo(this.map);

    this.marker.on('dragend', () => {
      const { lat, lng } = this.marker.getLatLng();
      this.handlePositionChange(lat, lng);
    });
  }

  private async handlePositionChange(lat: number, lng: number): Promise<void> {
    this.loadingAddress = true;
    const address = await reverseGeocode(lat, lng);
    this.currentAddress = address;
    this.loadingAddress = false;
    this.addressSelected.emit({ address, lat, lng });
  }
}
