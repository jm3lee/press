/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import { DataGrid, type GridColDef, type GridRowSelectionModel } from "@mui/x-data-grid";
import { useCallback, useMemo } from "react";

import type { CampaignSummary } from "../types";
import { formatTimestampForDisplay } from "../utils";

interface CampaignTableProps {
  campaigns: CampaignSummary[];
  loading: boolean;
  onEdit: (campaign: CampaignSummary) => void;
  onSelect?: (campaign: CampaignSummary | null) => void;
  selectedCampaignId?: string | null;
}

export const CampaignTable = ({
  campaigns,
  loading,
  onEdit,
  onSelect,
  selectedCampaignId,
}: CampaignTableProps): JSX.Element => {
  const rows = useMemo(
    () =>
      campaigns.map((campaign) => ({
        id: campaign.campaignId,
        campaign,
        campaignId: campaign.campaignId,
        name: campaign.name ?? "-",
        endTime: formatTimestampForDisplay(campaign.endTime),
        updatedAt: formatTimestampForDisplay(campaign.updatedAt),
      })),
    [campaigns],
  );

  const columns = useMemo<GridColDef[]>(
    () => [
      { field: "campaignId", headerName: "Campaign ID", flex: 1, minWidth: 150 },
      { field: "name", headerName: "Name", flex: 1, minWidth: 160 },
      { field: "endTime", headerName: "End time", flex: 1, minWidth: 200 },
      { field: "updatedAt", headerName: "Updated", flex: 1, minWidth: 200 },
      {
        field: "actions",
        headerName: "Actions",
        sortable: false,
        filterable: false,
        align: "right",
        flex: 0.6,
        minWidth: 160,
        renderCell: (params) => (
          <Button
            variant="outlined"
            size="small"
            onClick={(event) => {
              event.stopPropagation();
              onEdit(params.row.campaign as CampaignSummary);
            }}
          >
            Edit
          </Button>
        ),
      },
    ],
    [onEdit],
  );

  const handleRowSelectionModelChange = useCallback(
    (selection: GridRowSelectionModel) => {
      if (!onSelect) {
        return;
      }
      const [first] = selection;
      if (!first) {
        onSelect(null);
        return;
      }
      const candidate = campaigns.find((item) => item.campaignId === String(first));
      onSelect(candidate ?? null);
    },
    [campaigns, onSelect],
  );

  return (
    <Box sx={{ width: "100%" }}>
      <DataGrid
        rows={rows}
        columns={columns}
        autoHeight
        density="comfortable"
        disableRowSelectionOnClick={false}
        getRowId={(row) => row.id}
        loading={loading}
        pageSizeOptions={[5, 10, 25]}
        initialState={{
          pagination: { paginationModel: { pageSize: 10, page: 0 } },
          sorting: { sortModel: [{ field: "campaignId", sort: "asc" }] },
        }}
        onRowSelectionModelChange={handleRowSelectionModelChange}
        rowSelectionModel={selectedCampaignId ? [selectedCampaignId] : []}
      />
    </Box>
  );
};
