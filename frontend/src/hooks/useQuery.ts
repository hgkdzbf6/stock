/** React Query Hooks */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authService } from '@services/auth';
import { stockService } from '@services/stock';
import { marketService } from '@services/market';
import { strategyService } from '@services/strategy';

// 认证相关Hooks
export const useLogin = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      authService.login(username, password),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });
};

export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['user'],
    queryFn: () => authService.getCurrentUser(),
    retry: false,
  });
};

// 股票相关Hooks
export const useStockList = (params: { page?: number; page_size?: number; sector?: string } = {}) => {
  return useQuery({
    queryKey: ['stocks', params],
    queryFn: () => stockService.getStockList(params),
  });
};

export const useStock = (code: string) => {
  return useQuery({
    queryKey: ['stock', code],
    queryFn: () => stockService.getStock(code),
    enabled: !!code,
  });
};

export const useSearchStocks = (keyword: string, limit: number = 20) => {
  return useQuery({
    queryKey: ['stocks', 'search', keyword],
    queryFn: () => stockService.searchStocks(keyword, limit),
    enabled: keyword.length > 0,
  });
};

// 行情相关Hooks
export const useQuote = (code: string, refetchInterval?: number) => {
  return useQuery({
    queryKey: ['quote', code],
    queryFn: () => marketService.getQuote(code),
    enabled: !!code,
    refetchInterval: refetchInterval || false,
  });
};

export const useKlineData = (params: {
  code: string;
  freq?: string;
  start_date: string;
  end_date: string;
}) => {
  return useQuery({
    queryKey: ['kline', params],
    queryFn: () => marketService.getKlineData(params),
    enabled: !!params.code && !!params.start_date && !!params.end_date,
  });
};

export const useIndicators = (params: {
  code: string;
  freq?: string;
  start_date: string;
  end_date: string;
  indicators?: string[];
}) => {
  return useQuery({
    queryKey: ['indicators', params],
    queryFn: () => marketService.getIndicators(params),
    enabled: !!params.code && !!params.start_date && !!params.end_date,
  });
};

// 策略相关Hooks
export const useStrategies = () => {
  return useQuery({
    queryKey: ['strategies'],
    queryFn: () => strategyService.getStrategies(),
  });
};

export const useStrategy = (id: number) => {
  return useQuery({
    queryKey: ['strategy', id],
    queryFn: () => strategyService.getStrategy(id),
    enabled: !!id,
  });
};

export const useCreateStrategy = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: strategyService.createStrategy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] });
    },
  });
};

export const useUpdateStrategy = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      strategyService.updateStrategy(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] });
    },
  });
};

export const useDeleteStrategy = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: strategyService.deleteStrategy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] });
    },
  });
};

export const useRunBacktest = () => {
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      strategyService.runBacktest(id, data),
  });
};

export const useOptimizeStrategy = () => {
  return useMutation({
    mutationFn: ({ id, params }: { id: number; params: any }) =>
      strategyService.optimizeStrategy(id, params),
  });
};
