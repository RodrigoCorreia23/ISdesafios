import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    try {
        const formData = await req.formData();
        const file = formData.get("file") || null;

        console.log("File Received:", file);

        if (!file) {
            return NextResponse.json({ status: 400, message: "File not sent!" }, { status: 400 });
        }

        const backendFormData = new FormData();
        backendFormData.append("file", file);

        const requestOptions = {
            method: "POST",
            body: backendFormData,
        };

        const promise = await fetch(
            `${process.env.REST_API_BASE_URL}/api/upload-file/by-chunks/`,
            requestOptions
        );

        if (!promise.ok) {
            const errorBody = await promise.text();
            console.error("Backend Error:", errorBody);
            return NextResponse.json(
                { status: promise.status, message: errorBody || promise.statusText },
                { status: promise.status }
            );
        }

        const responseBody = await promise.json();
        return NextResponse.json(responseBody);
    } catch (e) {
        if (e instanceof Error) {
            console.error("Unhandled Error in route.ts:", e);
            return NextResponse.json(
                { status: 500, message: "Internal Server Error: " + e.message },
                { status: 500 }
            );
        } else {
            console.error("Unknown Error in route.ts:", e);
            return NextResponse.json(
                { status: 500, message: "An unknown error occurred." },
                { status: 500 }
            );
        }
    }
}