import { AfterViewInit, Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';
import * as L from 'leaflet';

import { reverseGeocode } from '../../utils/nominatim';

// Sao Paulo, used when geolocation is denied or unavailable.
const FALLBACK_CENTER: L.LatLngTuple = [-23.5505, -46.6333];

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
  imports: [],
  templateUrl: './address-picker.component.html',
  styleUrl: './address-picker.component.scss',
})
export class AddressPickerComponent implements AfterViewInit {
  @ViewChild('mapContainer', { static: true }) mapContainer!: ElementRef<HTMLDivElement>;
  @Output() addressSelected = new EventEmitter<SelectedAddress>();

  currentAddress = '';
  loadingAddress = false;

  private map!: L.Map;
  private marker!: L.Marker;

  ngAfterViewInit(): void {
    this.initMap(FALLBACK_CENTER);

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const center: L.LatLngTuple = [position.coords.latitude, position.coords.longitude];
          this.map.setView(center, 16);
          this.marker.setLatLng(center);
          this.handlePositionChange(center[0], center[1]);
        },
        () => this.handlePositionChange(FALLBACK_CENTER[0], FALLBACK_CENTER[1])
      );
    } else {
      this.handlePositionChange(FALLBACK_CENTER[0], FALLBACK_CENTER[1]);
    }
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
