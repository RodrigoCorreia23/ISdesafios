import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const request_body = await req.json();
    const warehouse = request_body?.search ?? ""; // Filtro enviado na requisição

    const headers = {
        "content-type": "application/json",
    };

    const requestBody = {
        query: `query GetMotorcycleSales {
            motorcycleSales${warehouse.length > 0 ? `(warehouse: "${warehouse}")` : ""} {
                id
                date
                warehouse
                client_type
                product_line
                latitude
                longitude
            }
        }`,
    };

    const options = {
        method: "POST",
        headers,
        body: JSON.stringify(requestBody),
    };

    try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_GRAPHQL_URL}/graphql/`, options);

        if (!res.ok) {
            console.error(`Erro: ${res.statusText}`);
            return NextResponse.json(
                { status: res.status, message: res.statusText },
                { status: res.status }
            );
        }

        const data = await res.json();

        if (!data?.data?.motorcycleSales) {
            return NextResponse.json(
                { status: 404, message: "Nenhum dado encontrado para o filtro solicitado." },
                { status: 404 }
            );
        }

        return NextResponse.json({
            data: {
                warehouses: data.data.motorcycleSales.map((sale: any) => ({
                    id: sale.id,
                    region: sale.warehouse,
                    product_line: sale.product_line,
                    latitude: sale.latitude,
                    longitude: sale.longitude,
                })),
            },
        });
    } catch (error) {
        console.error("Erro durante a comunicação com a API GraphQL:", error);
        return NextResponse.json(
            { status: 500, message: "Erro interno do servidor", details: error },
            { status: 500 }
        );
    }
}