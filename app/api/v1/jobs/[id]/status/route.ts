import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const response = await fetch(`${process.env.BACKEND_URL}/api/v1/jobs/${params.id}/status`)
    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Job status proxy error:", error)
    return NextResponse.json({ detail: "Failed to fetch job status" }, { status: 500 })
  }
}
