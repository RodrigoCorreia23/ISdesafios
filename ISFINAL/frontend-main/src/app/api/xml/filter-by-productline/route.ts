import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const request_body  = await req.json()

    const productLine = request_body?.product_line || "";

    if (!productLine) {
      return NextResponse.json(
        { error: "The 'product_line' field is required." },
        { status: 400 }
      );
    }

    const requestOptions = {
      method: "POST",
      body: JSON.stringify({ product_line: productLine }),
      headers: {
        "Content-Type": "application/json",
      },
    };

    try{
        const promise = await fetch(
            `${process.env.REST_API_BASE_URL}/api/filter-by-productline/`,
            requestOptions
        );

        if(!promise.ok){
            console.error("Error from backend:", promise.statusText);
            return NextResponse.json(
                { status: promise.status, message: promise.statusText },
                { status: promise.status }
            );
        }

        const xmlContent = await promise.text();
        return new Response(xmlContent, { headers: { "Content-Type": "text/xml" } });
  } catch (error) {
    console.error("An unexpected error occurred:", error);
    return NextResponse.json(
      { error: "An internal error occurred.", details: error },
      { status: 500 }
    );
  }
}
