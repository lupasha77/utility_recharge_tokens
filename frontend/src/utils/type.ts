export interface UtilityData {
  utility_type: string;  
  units_balance_brought_forward : number,
  units_purchased_to_date : number,
  units_used_to_date : number,
  cost_of_units_used_to_date : number,
  cost_of_units_purchased_to_date : number,
  units_balance_remaining_to_date : number,
  unit_price : number
  total_costs_to_date : number
  total_units_to_date : number
  }
  
  export interface UtilityStats {
    utility_type: string;
    total: number;
    used: number;
    purchased: number;
    cost: number;
    remaining: number;
    remaining_cost: number;
  }