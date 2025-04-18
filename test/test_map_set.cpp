#include "./test_lib/test_group.hpp"
#include "./test_lib/test_group.def.hpp"

namespace c4 {
namespace yml {


TEST(simple_set, emit)
{
    const char yaml[] = R"(!!set
? aa
? bb
? cc
)";
    std::string expected = R"(!!set
aa: 
bb: 
cc: 
)";
    Tree t = parse_in_arena(yaml);
    auto s = emitrs_yaml<std::string>(t);
    EXPECT_EQ(expected, s);
}


TEST(simple_set, emit_doc)
{
    const char yaml[] = R"(--- !!set
? aa
? bb
? cc
)";
    std::string expected = R"(--- !!set
aa: 
bb: 
cc: 
)";
    Tree t = parse_in_arena(yaml);
    auto s = emitrs_yaml<std::string>(t);
    EXPECT_EQ(expected, s);
}


//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------

CASE_GROUP(SIMPLE_SET)
{

ADD_CASE_TO_GROUP("doc as set, missing value",
R"(!!set
? a
? b
?
)",
N(MB, TL("!!set", L{N(KP|VN, "a", {}), N(KP|VN, "b", {}), N(KN|VN, {}, "")}))
);

ADD_CASE_TO_GROUP("doc as set, implicit",
R"(!!set
? a
? b
)",
N(MB, TL("!!set", L{N(KP|VN, "a", {}), N(KP|VN, "b", {})}))
);

ADD_CASE_TO_GROUP("doc as set",
R"(--- !!set
? aa
? bb
? cc
)",
N(STREAM, L{
  N(DOC|MB, TL("!!set", L{
    N(KP|VN, "aa", /*"~"*/{}),
    N(KP|VN, "bb", /*"~"*/{}),
    N(KP|VN, "cc", /*"~"*/{})
  }))
})
);

ADD_CASE_TO_GROUP("sets 2XXW",
R"(
--- !!set
? Mark McGwire
? Sammy Sosa
? Ken Griff
)",
N(STREAM, L{
  N(DOC|MB, TL("!!set", L{
    N(KP|VN, "Mark McGwire", /*"~"*/{}),
    N(KP|VN, "Sammy Sosa", /*"~"*/{}),
    N(KP|VN, "Ken Griff", /*"~"*/{}),
  }))
})
);

ADD_CASE_TO_GROUP("sets 2XXW, no set",
R"(
---
? Mark McGwire
? Sammy Sosa
? Ken Griff
)",
N(STREAM, L{
  N(DOC|MB, L{
    N(KP|VN, "Mark McGwire", /*"~"*/{}),
    N(KP|VN, "Sammy Sosa", /*"~"*/{}),
    N(KP|VN, "Ken Griff", /*"~"*/{}),
  })
})
);

ADD_CASE_TO_GROUP("sets 2XXW, no doc",
R"(!!set
? Mark McGwire
? Sammy Sosa
? Ken Griff
)",
N(MB, TL("!!set", L{
  N(KP|VN, "Mark McGwire", /*"~"*/{}),
  N(KP|VN, "Sammy Sosa", /*"~"*/{}),
  N(KP|VN, "Ken Griff", /*"~"*/{}),
}))
);

ADD_CASE_TO_GROUP("sets 2XXW, no doc, no set",
R"(
? Mark McGwire
? Sammy Sosa
? Ken Griff
)",
N(MB, L{
  N(KP|VN, "Mark McGwire", /*"~"*/{}),
  N(KP|VN, "Sammy Sosa", /*"~"*/{}),
  N(KP|VN, "Ken Griff", /*"~"*/{}),
})
);

}

} // namespace yml
} // namespace c4
