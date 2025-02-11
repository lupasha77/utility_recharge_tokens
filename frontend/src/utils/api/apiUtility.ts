//src/utils/api/apiUtility.ts
import { api } from "./axios";
import axios from "axios";

// src/utils/api/apiUtility.ts
export const getUtilityRates = async () => {
    try {
      const response = await api.get("/utilities/utility_unit_price");
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          error.response?.data?.error || 
          error.message || 
          'Failed to fetch utility rates'
        );
      }
      throw error;
    }
  };