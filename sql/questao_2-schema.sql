-- Questao 2 Schema
-- addresses.csv
CREATE TABLE IF NOT EXISTS "addresses" (
    "id" BIGINT PRIMARY KEY,
    "customer_id" BIGINT,
    "address_type" TEXT,
    "postal_code" TEXT,
    "street" TEXT,
    "number" BIGINT,
    "complement" TEXT,
    "district" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "is_primary" BOOLEAN
);

-- attributes.csv
CREATE TABLE IF NOT EXISTS "attributes" (
    "id" BIGINT PRIMARY KEY,
    "name" TEXT,
    "data_type" TEXT
);

-- brands.csv
CREATE TABLE IF NOT EXISTS "brands" (
    "id" BIGINT PRIMARY KEY,
    "name" TEXT,
    "country" TEXT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- categories.csv
CREATE TABLE IF NOT EXISTS "categories" (
    "id" BIGINT PRIMARY KEY,
    "name" TEXT,
    "slug" TEXT,
    "parent_category_id" BIGINT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- customers.csv
CREATE TABLE IF NOT EXISTS "customers" (
    "id" BIGINT PRIMARY KEY,
    "person_type" TEXT,
    "legal_name" TEXT,
    "trade_name" TEXT,
    "tax_id" TEXT,
    "state_registration" TEXT,
    "email" TEXT,
    "phone" TEXT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- employees.csv
CREATE TABLE IF NOT EXISTS "employees" (
    "id" BIGINT PRIMARY KEY,
    "full_name" TEXT,
    "cpf" TEXT,
    "email" TEXT,
    "role" TEXT,
    "primary_location_id" BIGINT,
    "hire_date" TIMESTAMP,
    "termination_date" TIMESTAMP,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- fiscal_invoices.csv
CREATE TABLE IF NOT EXISTS "fiscal_invoices" (
    "id" BIGINT PRIMARY KEY,
    "order_id" BIGINT,
    "nfe_number" TEXT,
    "nfe_access_key" TEXT,
    "series" BIGINT,
    "issued_at" TIMESTAMP,
    "status" TEXT,
    "total_amount" NUMERIC(18,2),
    "xml_storage_uri" TEXT,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- goods_receipts.csv
CREATE TABLE IF NOT EXISTS "goods_receipts" (
    "id" BIGINT PRIMARY KEY,
    "purchase_order_id" BIGINT,
    "received_by_employee_id" BIGINT,
    "received_at" TIMESTAMP,
    "notes" TEXT,
    "created_at" TIMESTAMP
);

-- goods_receipt_items.csv
CREATE TABLE IF NOT EXISTS "goods_receipt_items" (
    "id" BIGINT PRIMARY KEY,
    "goods_receipt_id" BIGINT,
    "purchase_order_item_id" BIGINT,
    "quantity_received" NUMERIC(18,6)
);

-- locations.csv
CREATE TABLE IF NOT EXISTS "locations" (
    "id" BIGINT PRIMARY KEY,
    "name" TEXT,
    "location_type" TEXT,
    "postal_code" TEXT,
    "street" TEXT,
    "number" BIGINT,
    "complement" TEXT,
    "district" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- orders.csv
CREATE TABLE IF NOT EXISTS "orders" (
    "id" BIGINT PRIMARY KEY,
    "order_number" TEXT,
    "channel" TEXT,
    "customer_id" BIGINT,
    "salesperson_id" BIGINT,
    "location_id" BIGINT,
    "status" TEXT,
    "subtotal" NUMERIC(18,2),
    "discount_amount" NUMERIC(18,2),
    "total" NUMERIC(18,2),
    "placed_at" TIMESTAMP,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- order_items.csv
CREATE TABLE IF NOT EXISTS "order_items" (
    "id" BIGINT PRIMARY KEY,
    "order_id" BIGINT,
    "product_variant_id" BIGINT,
    "quantity" BIGINT,
    "unit_price" NUMERIC(18,2),
    "icms_rate" NUMERIC(18,2),
    "ipi_rate" NUMERIC(18,2),
    "line_total" NUMERIC(18,2)
);

-- payments.csv
CREATE TABLE IF NOT EXISTS "payments" (
    "id" BIGINT PRIMARY KEY,
    "order_id" BIGINT,
    "method" TEXT,
    "installments" BIGINT,
    "amount" NUMERIC(18,2),
    "status" TEXT,
    "paid_at" TIMESTAMP,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- products.csv
CREATE TABLE IF NOT EXISTS "products" (
    "id" BIGINT PRIMARY KEY,
    "name" TEXT,
    "description" TEXT,
    "brand_id" BIGINT,
    "category_id" BIGINT,
    "ncm_code" TEXT,
    "unit_of_measure" TEXT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- product_suppliers.csv
CREATE TABLE IF NOT EXISTS "product_suppliers" (
    "product_variant_id" BIGINT,
    "supplier_id" BIGINT,
    "supplier_sku" TEXT,
    "last_quoted_cost" NUMERIC(18,2),
    "lead_time_days" BIGINT,
    "is_preferred" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- product_variants.csv
CREATE TABLE IF NOT EXISTS "product_variants" (
    "id" BIGINT PRIMARY KEY,
    "product_id" BIGINT,
    "sku" TEXT,
    "barcode_ean" TEXT,
    "sale_price" NUMERIC(18,2),
    "cost_price" NUMERIC(18,2),
    "weight_kg" NUMERIC(18,6),
    "icms_rate" NUMERIC(18,2),
    "ipi_rate" NUMERIC(18,2),
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- purchase_orders.csv
CREATE TABLE IF NOT EXISTS "purchase_orders" (
    "id" BIGINT PRIMARY KEY,
    "po_number" TEXT,
    "supplier_id" BIGINT,
    "buyer_id" BIGINT,
    "destination_location_id" BIGINT,
    "status" TEXT,
    "currency" TEXT,
    "subtotal" NUMERIC(18,2),
    "total" NUMERIC(18,2),
    "placed_at" TIMESTAMP,
    "expected_delivery_at" TIMESTAMP,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- purchase_order_items.csv
CREATE TABLE IF NOT EXISTS "purchase_order_items" (
    "id" BIGINT PRIMARY KEY,
    "purchase_order_id" BIGINT,
    "product_variant_id" BIGINT,
    "quantity_ordered" BIGINT,
    "unit_cost" NUMERIC(18,2),
    "line_total" NUMERIC(18,2)
);

-- returns.csv
CREATE TABLE IF NOT EXISTS "returns" (
    "id" BIGINT PRIMARY KEY,
    "return_number" TEXT,
    "order_id" BIGINT,
    "customer_id" BIGINT,
    "received_at_location_id" BIGINT,
    "status" TEXT,
    "reason" TEXT,
    "total_refund_amount" NUMERIC(18,2),
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- return_items.csv
CREATE TABLE IF NOT EXISTS "return_items" (
    "id" BIGINT PRIMARY KEY,
    "return_id" BIGINT,
    "order_item_id" BIGINT,
    "quantity" NUMERIC(18,6),
    "action" TEXT,
    "exchange_variant_id" BIGINT,
    "unit_refund_amount" NUMERIC(18,2)
);

-- stock_levels.csv
CREATE TABLE IF NOT EXISTS "stock_levels" (
    "product_variant_id" BIGINT,
    "location_id" BIGINT,
    "quantity_on_hand" NUMERIC(18,6),
    "reorder_point" TEXT,
    "updated_at" TIMESTAMP
);

-- stock_movements.csv
CREATE TABLE IF NOT EXISTS "stock_movements" (
    "id" BIGINT PRIMARY KEY,
    "product_variant_id" BIGINT,
    "location_id" BIGINT,
    "movement_type" TEXT,
    "quantity" NUMERIC(18,6),
    "reference_table" TEXT,
    "reference_id" BIGINT,
    "employee_id" BIGINT,
    "notes" TEXT,
    "occurred_at" TIMESTAMP,
    "created_at" TIMESTAMP
);

-- suppliers.csv
CREATE TABLE IF NOT EXISTS "suppliers" (
    "id" BIGINT PRIMARY KEY,
    "legal_name" TEXT,
    "trade_name" TEXT,
    "country" TEXT,
    "tax_id" TEXT,
    "tax_id_type" TEXT,
    "email" TEXT,
    "phone" TEXT,
    "contact_name" TEXT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- variant_attribute_values.csv
CREATE TABLE IF NOT EXISTS "variant_attribute_values" (
    "product_variant_id" BIGINT,
    "attribute_id" BIGINT,
    "value" TEXT
);
