// Transform backend data to component format
import { UtilityData } from '../utils/type'; // Adjust the import path as necessary

interface BackendUtilityData {
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

export const transformUtilityData = (data: BackendUtilityData): UtilityData => {

  return {

    utility_type: data.utility_type,

    units_balance_brought_forward: data.units_balance_brought_forward,

    units_purchased_to_date: data.units_purchased_to_date,

    units_used_to_date: data.units_used_to_date,

    cost_of_units_used_to_date: data.cost_of_units_used_to_date,

    cost_of_units_purchased_to_date: data.cost_of_units_purchased_to_date,

    units_balance_remaining_to_date: data.units_balance_remaining_to_date,

    unit_price: data.unit_price,

    total_costs_to_date: data.total_costs_to_date,

    total_units_to_date: data.total_units_to_date

  };
};