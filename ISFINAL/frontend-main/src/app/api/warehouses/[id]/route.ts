import { NextRequest, NextResponse } from "next/server";

export async function PUT(req: NextRequest) {
    const request_body = await req.json();
    const id = req.nextUrl.pathname.split("/")[3];

    const headers = {
        "content-type": "application/json",
    };

    const requestBody = {
        query: `mutation UpdateMotorcycleSale {
            updateMotorcycleSale(
                id: ${id}, 
                latitude: ${request_body.latitude}, 
                longitude: ${request_body.longitude}
            ) {
                motorcycleSales {
                    id
                    latitude
                    longitude
                    warehouse
                    product_line
                }
            }
        }`,
    };

    const options = {
        method: "POST",
        headers,
        body: JSON.stringify(requestBody),
    };

    try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_GRAPHQL_URL}/graphql/`, options);

        if (!response.ok) {
            console.error(`Erro: ${response.statusText}`);
            return NextResponse.json(
                { status: response.status, message: response.statusText },
                { status: response.status }
            );
        }

        const data = await response.json();

        if (!data?.data?.updateMotorcycleSale?.motorcycleSales) {
            return NextResponse.json(
                { status: 404, message: "Registo não foi atualizado ou não encontrado." },
                { status: 404 }
            );
        }

        return NextResponse.json({
            message: "Registo atualizado com sucesso.",
            data: {
                id: data.data.updateMotorcycleSale.motorcycleSales.id,
                latitude: data.data.updateMotorcycleSale.motorcycleSales.latitude,
                longitude: data.data.updateMotorcycleSale.motorcycleSales.longitude,
                warehouse: data.data.updateMotorcycleSale.motorcycleSales.warehouse,
                product_line: data.data.updateMotorcycleSale.motorcycleSales.product_line,
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