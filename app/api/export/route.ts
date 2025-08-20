import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Forward request to FastAPI backend
    const response = await fetch(`${process.env.BACKEND_URL}/export/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: request.headers.get("Authorization") || "",
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(error, { status: response.status })
    }

    // Stream the file response
    const contentType = response.headers.get("content-type") || "application/octet-stream"
    const contentDisposition = response.headers.get("content-disposition") || ""

    return new NextResponse(response.body, {
      status: 200,
      headers: {
        "Content-Type": contentType,
        "Content-Disposition": contentDisposition,
      },
    })
  } catch (error) {
    return NextResponse.json({ detail: "Export failed" }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    // Forward request to get export formats
    const response = await fetch(`${process.env.BACKEND_URL}/export/formats`)
    const data = await response.json()

    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json({ detail: "Failed to get export formats" }, { status: 500 })
  }
}
