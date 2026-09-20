import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  listProducts,
  listManageableProducts,
  pilotToken,
  pilotOperatorToken,
  customerIntake,
  createGuest,
  generateRecommendations,
  listRecommendationsByCase,
  createSale,
  getTotalSales,
  listSalesByCustomer,
  getCustomerById,
  searchCustomers,
  getInventoryByProduct,
} from "../api/client";
