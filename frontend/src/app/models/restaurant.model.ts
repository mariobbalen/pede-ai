export interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: string;
  is_available: boolean;
}

export interface RestaurantSummary {
  id: string;
  name: string;
  description: string;
  address: string;
  is_active: boolean;
}

export interface RestaurantDetail extends RestaurantSummary {
  menu_items: MenuItem[];
}
