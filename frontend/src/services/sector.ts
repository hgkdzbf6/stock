/** 板块服务 */
import api from './api';

export interface Sector {
  code: string;
  name: string;
  description?: string;
}

export const sectorService = {
  /** 获取板块列表 */
  async getSectorList(): Promise<Sector[]> {
    const response = await api.get<{ code: number; message: string; data: Sector[] }>('/sector/list');
    return response.data;
  },

  /** 根据板块获取股票列表 */
  async getStocksBySector(
    sectorCode: string,
    page: number = 1,
    pageSize: number = 20
  ) {
    const response = await api.get<{
      code: number;
      message: string;
      data: {
        items: any[];
        total: number;
        page: number;
        page_size: number;
      };
    }>(`/sector/${sectorCode}/stocks`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
};

export default sectorService;