from chains.audit_chain import analyze_module
from langchain_community.chat_models import ChatOpenAI
import asyncio
from langchain.callbacks import get_openai_callback



async def process_clause_async(clause, text, llm):
    def sync_callback_wrapper():
        with get_openai_callback() as cb:
            audit_chain = analyze_module(llm)
            result = audit_chain.run(
                text=text,
                control_json=clause.to_json(orient='records', indent=2)
            )
            return {
                "result": result,
                "tokens": cb.total_tokens,
                "cost": cb.total_cost,
                "controls": len(clause)
            }

    return await asyncio.to_thread(sync_callback_wrapper)

async def run_all_clauses(text,llm,clauses):
    results = []
    total_tokens = 0
    total_cost = 0.0

    tasks = [process_clause_async(clause, text, llm) for clause in clauses]
    clause_results = await asyncio.gather(*tasks)

    for data in clause_results:
        results.append(data["result"])
        total_tokens += data["tokens"]
        total_cost += data["cost"]
        print(f"🔎 Clause Processed: {data['controls']} controls")
        print(f"🧠 Tokens used: {data['tokens']}")
        print(f"💵 Cost: ${data['cost']:.6f}")

    print("\n✅ All clauses processed (async).")
    print(f"🔢 Total tokens used: {total_tokens}")
    print(f"💰 Total cost: ${total_cost:.6f}")

    return results

