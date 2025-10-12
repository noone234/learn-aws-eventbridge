import type { EDI4010_204_Event } from "../../../../app/lambdas/events/4010/4010_204Event";

/** TransNoble delivery, live unload */
export const test204TransNobleDeliveryLiveUnload: EDI4010_204_Event = {
  event: {
    version: "0",
    id: "caa88d0f-4b80-f74c-4cdf-9451448a6955",
    "detail-type": "transaction.processed.v2",
    source: "stedi.core",
    account: "464028090390",
    time: "2024-03-19T14:43:06Z",
    region: "us-east-1",
    resources: [
      "https://core.us.stedi.com/2023-08-01/transactions/af530c9a-9c54-4637-80ea-1f242a6672d2",
    ],
    detail: {
      transactionId: "af530c9a-9c54-4637-80ea-1f242a6672d2",
      direction: "INBOUND",
      mode: "production",
      fileExecutionId: "cb99652c-d50e-46cc-9951-2d94a52c455f",
      processedAt: "2024-03-19T14:43:06.331Z",
      fragments: null,
      artifacts: [
        {
          artifactType: "application/edi-x12",
          usage: "input",
          url: "https://core.us.stedi.com/2023-08-01/transactions/af530c9a-9c54-4637-80ea-1f242a6672d2/input",
          sizeBytes: 806,
          model: "transaction",
        },
        {
          artifactType: "application/json",
          usage: "output",
          url: "https://core.us.stedi.com/2023-08-01/transactions/af530c9a-9c54-4637-80ea-1f242a6672d2/output",
          sizeBytes: 4280,
          model: "transaction",
        },
      ],
      partnership: {
        partnershipId: "ModalView_TDIS",
        partnershipType: "x12",
        sender: {
          profileId: "TDIS",
        },
        receiver: {
          profileId: "ModalView",
        },
      },
      x12: {
        transactionSetting: {
          guideId: "01HGB5Q0VVGFRFR65NMP6B8ZX9",
          transactionSettingId: "01HGH4N7D8VGCXGVD97JTNKK1N",
        },
        metadata: {
          interchange: {
            acknowledgmentRequestedCode: "0",
            controlNumber: 5810,
          },
          functionalGroup: {
            controlNumber: 5810,
            release: "004010",
            date: "2024-03-19",
            time: "10:42",
            functionalIdentifierCode: "SM",
          },
          transaction: {
            controlNumber: "5810001",
            transactionSetIdentifier: "204",
          },
          receiver: {
            applicationCode: "MODALVIEW",
            isa: {
              qualifier: "ZZ",
              id: "MODALVIEW",
            },
          },
          sender: {
            applicationCode: "TDIS",
            isa: {
              qualifier: "02",
              id: "TDIS",
            },
          },
        },
      },
      connectionId: "01HF7MP3Z2PHRG2MGTKQYC5VG0",
    },
  },
  artifact: {
    artifactType: "application/json",
    usage: "output",
    attachedReason: "WITHIN_SIZE_LIMIT",
    detail: {
      heading: {
        transaction_set_header_ST: {
          transaction_set_identifier_code_01: "204",
          transaction_set_control_number_02: 190001,
        },
        beginning_segment_for_shipment_information_transaction_B2: {
          standard_carrier_alpha_code_02: "TNQG",
          shipment_identification_number_04: "417167540303N",
          shipment_method_of_payment_06: "PP",
        },
        set_purpose_B2A: {
          transaction_set_purpose_code_01: "04",
          application_type_02: "LT",
        },
        business_instructions_and_reference_number_L11: [
          {
            reference_identification_01: "3208058883",
            reference_identification_qualifier_02: "BM",
          },
          {
            reference_identification_01: "2431946131",
            reference_identification_qualifier_02: "BT",
          },
          {
            reference_identification_01: "0312357",
            reference_identification_qualifier_02: "CO",
          },
          {
            reference_identification_01: "MUST CHECK IN AS CW CARRIERS",
            reference_identification_qualifier_02: "NO",
          },
          {
            reference_identification_01: "4504",
            reference_identification_qualifier_02: "RE",
          },
        ],
        note_special_instruction_NTE: [
          {
            description_02:
              "PAPERWORK REQUIREMENTS:Shipper:  BOLConsignee:  signed BOL or POD;",
          },
        ],
        equipment_details_N7_loop: [
          {
            equipment_details_N7: {
              equipment_initial_01: "EMHU",
              equipment_number_02: "300850",
              equipment_description_code_11: "CN",
              standard_carrier_alpha_code_12: "EMP",
              equipment_length_15: 5300,
            },
          },
        ],
      },
      detail: {
        stop_off_details_S5_loop: [
          {
            stop_off_details_S5: {
              stop_sequence_number_01: 1,
              stop_reason_code_02: "CL",
            },
            date_time_G62: [
              {
                date_qualifier_01: "37",
                date_02: "2024-12-19",
                time_qualifier_03: "2",
                time_04: "00:01",
                time_code_05: "ED",
              },
              {
                date_qualifier_01: "38",
                date_02: "2024-12-19",
                time_qualifier_03: "2",
                time_04: "15:36",
                time_code_05: "ED",
              },
            ],
            name_N1_loop: {
              name_N1: {
                entity_identifier_code_01: "RD",
                name_02: "NS HARRISBURG RAMP",
              },
              address_information_N3: [
                {
                  address_information_01: "3500 INDUSTRIAL ROAD",
                },
              ],
              geographic_location_N4: {
                city_name_01: "HARRISBURG",
                state_or_province_code_02: "PA",
                postal_code_03: "17110",
              },
            },
          },
          {
            stop_off_details_S5: {
              stop_sequence_number_01: 2,
              stop_reason_code_02: "CU", // Complete Unload = live unload
            },
            date_time_G62: [
              {
                date_qualifier_01: "53",
                date_02: "2024-12-19",
                time_qualifier_03: "3",
                time_04: "16:00",
                time_code_05: "ED",
              },
              {
                date_qualifier_01: "54",
                date_02: "2024-12-19",
                time_qualifier_03: "3",
                time_04: "16:00",
                time_code_05: "ED",
              },
            ],
            name_N1_loop: {
              name_N1: {
                entity_identifier_code_01: "CN",
                name_02: "MECHANICSBURG-US-RENTAL-XPO",
              },
              address_information_N3: [
                {
                  address_information_01: "600 HUNTER LANE",
                },
              ],
              geographic_location_N4: {
                city_name_01: "MIDDLETOWN",
                state_or_province_code_02: "PA",
                postal_code_03: "17057",
              },
            },
          },
          {
            stop_off_details_S5: {
              stop_sequence_number_01: 3,
              stop_reason_code_02: "DR",
            },
            date_time_G62: [
              {
                date_qualifier_01: "53",
                date_02: "2024-11-22",
                time_qualifier_03: "3",
                time_04: "07:02",
                time_code_05: "ED",
              },
              {
                date_qualifier_01: "54",
                date_02: "2024-11-22",
                time_qualifier_03: "3",
                time_04: "07:02",
                time_code_05: "ED",
              },
            ],
            name_N1_loop: {
              name_N1: {
                entity_identifier_code_01: "RD",
                name_02: "NS RUTHERFORD RAMP",
              },
              address_information_N3: [
                {
                  address_information_01: "5050 PAXTON STREET",
                },
              ],
              geographic_location_N4: {
                city_name_01: "HARRISBURG",
                state_or_province_code_02: "PA",
                postal_code_03: "17111",
              },
            },
          },
        ],
      },
      summary: {
        total_weight_and_charges_L3: {
          weight_01: 42247,
          weight_qualifier_02: "G",
          freight_rate_03: 185,
          rate_value_qualifier_04: "FR",
          charge_05: 43.48,
          special_charge_or_allowance_code_08: "405",
          lading_quantity_11: 1,
        },
        transaction_set_trailer_SE: {
          number_of_included_segments_01: 30,
          transaction_set_control_number_02: 190001,
        },
      },
    },
  },
};

/** TransNoble delivery, drop and hook */
export const test204TransNobleDeliveryDropHook: EDI4010_204_Event = {
  event: {
    version: "0",
    id: "caa88d0f-4b80-f74c-4cdf-9451448a6955",
    "detail-type": "transaction.processed.v2",
    source: "stedi.core",
    account: "464028090390",
    time: "2024-03-19T14:43:06Z",
    region: "us-east-1",
    resources: [
      "https://core.us.stedi.com/2023-08-01/transactions/af530c9a-9c54-4637-80ea-1f242a6672d2",
    ],
    detail: {
      transactionId: "af530c9a-9c54-4637-80ea-1f242a6672d2",
      direction: "INBOUND",
      mode: "production",
      fileExecutionId: "cb99652c-d50e-46cc-9951-2d94a52c455f",
      processedAt: "2024-03-19T14:43:06.331Z",
      fragments: null,
      artifacts: [
        {
          artifactType: "application/edi-x12",
          usage: "input",
          url: "https://core.us.stedi.com/2023-08-01/transactions/af530c9a-9c54-4637-80ea-1f242a6672d2/input",
          sizeBytes: 806,
          model: "transaction",
        },
        {
          artifactType: "application/json",
          usage: "output",
          url: "https://core.us.stedi.com/2023-08-01/transactions/af530c9a-9c54-4637-80ea-1f242a6672d2/output",
          sizeBytes: 4280,
          model: "transaction",
        },
      ],
      partnership: {
        partnershipId: "ModalView_TDIS",
        partnershipType: "x12",
        sender: {
          profileId: "TDIS",
        },
        receiver: {
          profileId: "ModalView",
        },
      },
      x12: {
        transactionSetting: {
          guideId: "01HGB5Q0VVGFRFR65NMP6B8ZX9",
          transactionSettingId: "01HGH4N7D8VGCXGVD97JTNKK1N",
        },
        metadata: {
          interchange: {
            acknowledgmentRequestedCode: "0",
            controlNumber: 5810,
          },
          functionalGroup: {
            controlNumber: 5810,
            release: "004010",
            date: "2024-03-19",
            time: "10:42",
            functionalIdentifierCode: "SM",
          },
          transaction: {
            controlNumber: "5810001",
            transactionSetIdentifier: "204",
          },
          receiver: {
            applicationCode: "MODALVIEW",
            isa: {
              qualifier: "ZZ",
              id: "MODALVIEW",
            },
          },
          sender: {
            applicationCode: "TDIS",
            isa: {
              qualifier: "02",
              id: "TDIS",
            },
          },
        },
      },
      connectionId: "01HF7MP3Z2PHRG2MGTKQYC5VG0",
    },
  },
  artifact: {
    artifactType: "application/json",
    usage: "output",
    attachedReason: "WITHIN_SIZE_LIMIT",
    detail: {
      heading: {
        transaction_set_header_ST: {
          transaction_set_identifier_code_01: "204",
          transaction_set_control_number_02: 190001,
        },
        beginning_segment_for_shipment_information_transaction_B2: {
          standard_carrier_alpha_code_02: "TNQG",
          shipment_identification_number_04: "417167540303N",
          shipment_method_of_payment_06: "PP",
        },
        set_purpose_B2A: {
          transaction_set_purpose_code_01: "04",
          application_type_02: "LT",
        },
        business_instructions_and_reference_number_L11: [
          {
            reference_identification_01: "3208058883",
            reference_identification_qualifier_02: "BM",
          },
          {
            reference_identification_01: "2431946131",
            reference_identification_qualifier_02: "BT",
          },
          {
            reference_identification_01: "0312357",
            reference_identification_qualifier_02: "CO",
          },
          {
            reference_identification_01: "MUST CHECK IN AS CW CARRIERS",
            reference_identification_qualifier_02: "NO",
          },
          {
            reference_identification_01: "4504",
            reference_identification_qualifier_02: "RE",
          },
          {
            reference_identification_01: "agRefNumber",
            reference_identification_qualifier_02: "AG",
          },
        ],
        note_special_instruction_NTE: [
          {
            description_02:
              "PAPERWORK REQUIREMENTS:Shipper:  BOLConsignee:  signed BOL or POD;",
          },
        ],
        equipment_details_N7_loop: [
          {
            equipment_details_N7: {
              equipment_initial_01: "EMHU",
              equipment_number_02: "300850",
              equipment_description_code_11: "CN",
              standard_carrier_alpha_code_12: "EMP",
              equipment_length_15: 5300,
            },
          },
        ],
      },
      detail: {
        stop_off_details_S5_loop: [
          {
            stop_off_details_S5: {
              stop_sequence_number_01: 1,
              stop_reason_code_02: "CL",
            },
            date_time_G62: [
              {
                date_qualifier_01: "37",
                date_02: "2024-12-19",
                time_qualifier_03: "2",
                time_04: "00:01",
                time_code_05: "ED",
              },
              {
                date_qualifier_01: "38",
                date_02: "2024-12-19",
                time_qualifier_03: "2",
                time_04: "15:36",
                time_code_05: "ED",
              },
            ],
            name_N1_loop: {
              name_N1: {
                entity_identifier_code_01: "RD",
                name_02: "NS HARRISBURG RAMP",
              },
              address_information_N3: [
                {
                  address_information_01: "3500 INDUSTRIAL ROAD",
                },
              ],
              geographic_location_N4: {
                city_name_01: "HARRISBURG",
                state_or_province_code_02: "PA",
                postal_code_03: "17110",
              },
            },
          },
          {
            stop_off_details_S5: {
              stop_sequence_number_01: 2,
              stop_reason_code_02: "SU", // spot unload = drop and hook
            },
            date_time_G62: [
              {
                date_qualifier_01: "53",
                date_02: "2024-12-19",
                time_qualifier_03: "3",
                time_04: "16:00",
                time_code_05: "ED",
              },
              {
                date_qualifier_01: "54",
                date_02: "2024-12-19",
                time_qualifier_03: "3",
                time_04: "16:00",
                time_code_05: "ED",
              },
            ],
            name_N1_loop: {
              name_N1: {
                entity_identifier_code_01: "CN",
                name_02: "MECHANICSBURG-US-RENTAL-XPO",
              },
              address_information_N3: [
                {
                  address_information_01: "600 HUNTER LANE",
                },
              ],
              geographic_location_N4: {
                city_name_01: "MIDDLETOWN",
                state_or_province_code_02: "PA",
                postal_code_03: "17057",
              },
            },
          },
          {
            stop_off_details_S5: {
              stop_sequence_number_01: 3,
              stop_reason_code_02: "DR",
            },
            date_time_G62: [
              {
                date_qualifier_01: "53",
                date_02: "2024-11-22",
                time_qualifier_03: "3",
                time_04: "07:02",
                time_code_05: "ED",
              },
              {
                date_qualifier_01: "54",
                date_02: "2024-11-22",
                time_qualifier_03: "3",
                time_04: "07:02",
                time_code_05: "ED",
              },
            ],
            name_N1_loop: {
              name_N1: {
                entity_identifier_code_01: "RD",
                name_02: "NS RUTHERFORD RAMP",
              },
              address_information_N3: [
                {
                  address_information_01: "5050 PAXTON STREET",
                },
              ],
              geographic_location_N4: {
                city_name_01: "HARRISBURG",
                state_or_province_code_02: "PA",
                postal_code_03: "17111",
              },
            },
          },
        ],
      },
      summary: {
        total_weight_and_charges_L3: {
          weight_01: 42247,
          weight_qualifier_02: "G",
          freight_rate_03: 185,
          rate_value_qualifier_04: "FR",
          charge_05: 43.48,
          special_charge_or_allowance_code_08: "405",
          lading_quantity_11: 1,
        },
        transaction_set_trailer_SE: {
          number_of_included_segments_01: 30,
          transaction_set_control_number_02: 190001,
        },
      },
    },
  },
};
